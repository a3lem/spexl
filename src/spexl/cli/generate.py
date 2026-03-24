# [AI]
# Context: idempotent-init change
# Intent: single idempotent init command with .spexl.toml config, --remove flag, content-hash refresh
# Assumes: tomllib available (stdlib 3.11+), no external TOML writer needed

from __future__ import annotations

import argparse
import os
import typing as T
from pathlib import Path

from spexl.config import (
    CONFIG_FILENAME,
    SpecsLocation,
    find_nearest_config,
    read_config,
    update_config,
    write_config,
)
from spexl.errors import SpexlError
from spexl.generate.compose import SKILL_MANIFESTS, compose_skill
from spexl.templates import read_template

SUPPORTED_TARGETS = ("claude",)

# Agent template files to install
AGENT_TEMPLATES = ("spec-critic.md", "spec-sync.md")


def _display_path(abs_path: Path) -> str:
    """Return a path string relative to the user's cwd for display."""
    return os.path.relpath(abs_path.resolve(), Path.cwd().resolve())


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_init = subparsers.add_parser(
        "init", help="Install or refresh spexl agent integration files"
    )
    p_init.add_argument(
        "target",
        nargs="?",
        metavar="AGENT",
        help="Target agent framework {claude}",
    )
    p_init.add_argument(
        "--remove",
        action="store_true",
        help="Remove all spexl-managed files",
    )
    p_init.set_defaults(func=cmd_init)


def _find_existing_config() -> tuple[Path, dict[str, T.Any]] | None:
    """Try to find an existing config. Returns None if not found (no error)."""
    try:
        cfg = find_nearest_config()
        raw = read_config(cfg.toml_path) if cfg.toml_path.stat().st_size > 0 else {}
        return (cfg.toml_path, raw)
    except SpexlError:
        return None


def _scaffold_project(project_root: Path) -> None:
    """Create .spexl.toml with defaults and specs directory structure."""
    config_path = project_root / CONFIG_FILENAME
    specs_loc = SpecsLocation()
    specs_dir = project_root / specs_loc.dir_path
    changes_dir = specs_dir / specs_loc.changes_dir
    reference_dir = specs_dir / specs_loc.reference_dir

    write_config(config_path)

    changes_dir.mkdir(parents=True, exist_ok=True)
    reference_dir.mkdir(parents=True, exist_ok=True)

    print(f"  created    {_display_path(config_path)}")
    print(f"  created    {_display_path(changes_dir)}/")
    print(f"  created    {_display_path(reference_dir)}/")
    print("\nProject initialized.")


def cmd_init(args: T.Any) -> None:
    if args.remove:
        _do_remove()
        return

    config_result = _find_existing_config()

    if args.target:
        if args.target not in SUPPORTED_TARGETS:
            raise SpexlError(
                f"Unknown target '{args.target}'. Supported targets: {', '.join(SUPPORTED_TARGETS)}"
            )
        if config_result:
            config_path, config = config_result
            project_root = config_path.parent
            if args.target in config.get("agents", {}):
                # Already installed, refresh
                install_path = Path(config["agents"][args.target]["install_path"])
                _do_refresh(project_root, install_path, args.target)
            else:
                # Config exists but target not installed yet
                install_path = _default_install_path(args.target)
                _do_install(project_root, install_path, args.target, config_path)
        else:
            # Fresh install in cwd
            project_root = Path.cwd()
            install_path = _default_install_path(args.target)
            _do_install(project_root, install_path, args.target, config_path=None)
    else:
        # No target argument
        local_config = Path.cwd() / CONFIG_FILENAME
        if not local_config.is_file():
            # No .spexl.toml in cwd -- scaffold here
            _scaffold_project(Path.cwd())
            # Warn if a parent also has .spexl.toml
            if config_result:
                parent_path = config_result[0]
                print(f"note: parent project found at {_display_path(parent_path.parent)}/")
            return

        if not config_result:
            _scaffold_project(Path.cwd())
            return

        config_path, config = config_result
        project_root = config_path.parent
        agents = config.get("agents", {})
        if not agents:
            raise SpexlError(
                f"No agents configured in {config_path}. "
                f"Run 'spexl init <target>' to install."
            )
        for target_name, target_config in agents.items():
            install_path = Path(target_config["install_path"])
            _do_refresh(project_root, install_path, target_name)


def _default_install_path(target: str) -> Path:
    """Return the default install path for a target."""
    if target == "claude":
        return Path(".claude")
    assert False, f"No default install path for target: {target}"


def _managed_files(install_path: Path) -> dict[Path, T.Callable[[], str]]:
    """Map of relative file paths to content-generating functions.

    All paths are relative to the project root.
    """
    files: dict[Path, T.Callable[[], str]] = {}
    for action_name in SKILL_MANIFESTS:
        p = install_path / "skills" / f"spexl-{action_name}" / "SKILL.md"
        files[p] = lambda a=action_name: compose_skill(a)
    for agent_name in AGENT_TEMPLATES:
        p = install_path / "agents" / agent_name
        files[p] = lambda n=agent_name: read_template("agents", n)
    files[install_path / "rules" / "spexl.md"] = lambda: read_template("prime", "prime.md")
    return files


def _do_install(
    project_root: Path,
    install_path: Path,
    target: str,
    config_path: Path | None,
) -> None:
    """Fresh install: write all managed files and create/update config."""
    files = _managed_files(install_path)
    created = 0
    for rel_path, content_fn in files.items():
        abs_path = project_root / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(content_fn())
        print(f"  created    {_display_path(abs_path)}")
        created += 1

    # Write or update config
    if config_path:
        update_config(config_path, target, str(install_path))
    else:
        config_path = project_root / CONFIG_FILENAME
        write_config(config_path, agents={target: str(install_path)})
    print(f"  created    {_display_path(config_path)}")

    print(f"\n{created} files created")


def _do_refresh(project_root: Path, install_path: Path, _target: str) -> None:
    """Idempotent refresh: overwrite only files whose content differs."""
    files = _managed_files(install_path)
    changed = 0
    unchanged = 0
    for rel_path, content_fn in files.items():
        abs_path = project_root / rel_path
        new_content = content_fn()
        if abs_path.is_file() and abs_path.read_text() == new_content:
            print(f"  unchanged  {_display_path(abs_path)}")
            unchanged += 1
        else:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(new_content)
            print(f"  changed    {_display_path(abs_path)}")
            changed += 1

    print(f"\n{changed} files changed, {unchanged} unchanged")


def _do_remove() -> None:
    """Remove all spexl-managed files. Never touches specs/."""
    config_result = _find_existing_config()
    if not config_result:
        print("Nothing to remove")
        return

    config_path, config = config_result
    project_root = config_path.parent
    removed = 0

    for _, target_config in config.get("agents", {}).items():
        install_path = Path(target_config["install_path"])
        files = _managed_files(install_path)
        for rel_path in files:
            abs_path = project_root / rel_path
            if abs_path.is_file():
                abs_path.unlink()
                print(f"  removed    {_display_path(abs_path)}")
                removed += 1

        # Prune empty directories bottom-up within install path
        _prune_empty_dirs(project_root / install_path)

    # Remove config file
    config_path.unlink()
    print(f"  removed    {_display_path(config_path)}")
    removed += 1

    print(f"\n{removed} files removed")


def _prune_empty_dirs(root: Path) -> None:
    """Remove empty directories bottom-up. Stops at root (does not remove root itself)."""
    if not root.is_dir():
        return
    for child in sorted(root.rglob("*"), reverse=True):
        if child.is_dir() and not any(child.iterdir()):
            child.rmdir()
