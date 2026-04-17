# [AI]
# Context: split-init-install -- `init` scaffolds the project, `install` manages agent assets
# Intent: two CLI entry points backed by one module; init is agent-free, install is scaffold-free
# Assumes: skills live in importlib.resources spexl.content.skills, agents in spexl.content.agents

from __future__ import annotations

import argparse
import importlib.resources
import os
import sys
import typing as T
from importlib.resources.abc import Traversable
from pathlib import Path

from spexl.config import (
    CONFIG_FILENAME,
    ProjectConfig,
    SpecsLocation,
    find_nearest_config,
    read_config,
    update_config,
    write_config,
)
from spexl.errors import SpexlError

SUPPORTED_TARGETS = ("claude",)


def _display_path(abs_path: Path) -> str:
    return os.path.relpath(abs_path.resolve(), Path.cwd().resolve())


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_init = subparsers.add_parser(
        "init", help="Scaffold a spexl project (.spexl.toml + specs/)"
    )
    # [AI]
    # Context: split-init-install
    # Intent: accept a positional argument only to give a helpful error redirecting to `install`,
    #         rather than argparse's generic "unrecognized arguments" message
    p_init.add_argument(
        "target",
        nargs="?",
        help=argparse.SUPPRESS,
    )
    p_init.set_defaults(func=cmd_init)

    p_install = subparsers.add_parser(
        "install", help="Install or refresh spexl agent integration files"
    )
    p_install.add_argument(
        "target",
        nargs="?",
        metavar="AGENT",
        help="Target agent framework {claude}",
    )
    p_install.add_argument(
        "--remove",
        action="store_true",
        help="Remove all spexl-managed agent files",
    )
    p_install.set_defaults(func=cmd_install)


def _find_existing_config() -> tuple[Path, dict[str, T.Any]] | None:
    try:
        cfg = find_nearest_config()
        raw = read_config(cfg.toml_path) if cfg.toml_path.stat().st_size > 0 else {}
        return (cfg.toml_path, raw)
    except SpexlError:
        return None


def _ensure_specs_dirs(project_root: Path) -> list[Path]:
    specs_loc = SpecsLocation()
    specs_dir = project_root / specs_loc.dir_path
    changes_dir = specs_dir / specs_loc.changes_dir
    reference_dir = specs_dir / specs_loc.reference_dir

    created: list[Path] = []
    for d in (changes_dir, reference_dir):
        if not d.is_dir():
            d.mkdir(parents=True, exist_ok=True)
            created.append(d)
    return created


def _scaffold_project(project_root: Path) -> None:
    config_path = project_root / CONFIG_FILENAME
    config_existed = config_path.is_file()
    if not config_existed:
        write_config(config_path)
        print(f"  created    {_display_path(config_path)}")

    for d in _ensure_specs_dirs(project_root):
        print(f"  created    {_display_path(d)}/")

    print("\nProject initialized." if not config_existed else "")


def cmd_init(args: T.Any) -> None:
    if args.target:
        raise SpexlError(
            f"'spexl init' takes no arguments. "
            f"Use 'spexl install {args.target}' to install agent assets."
        )

    cwd = Path.cwd()
    local_config = cwd / CONFIG_FILENAME

    # [AI]
    # Context: split-init-install refinement
    # Intent: when the directory is fully initialized (config + resolved specs dir both present),
    #         exit 0 with a stderr notice instead of silently no-oping
    if local_config.is_file():
        cfg = ProjectConfig.from_toml(local_config)
        if cfg.specs_dir.is_dir():
            print("spexl already initialized in this directory", file=sys.stderr)
            return

    _scaffold_project(cwd)

    parent = _find_parent_config(cwd)
    if parent is not None and parent != local_config:
        print(f"note: parent project found at {_display_path(parent.parent)}/")


def _find_parent_config(start: Path) -> Path | None:
    current = start.resolve().parent
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        if (current / ".git").exists():
            return None
        parent = current.parent
        if parent == current:
            return None
        current = parent


def cmd_install(args: T.Any) -> None:
    if args.remove:
        _do_remove()
        return

    config_result = _find_existing_config()

    if args.target:
        if args.target not in SUPPORTED_TARGETS:
            raise SpexlError(
                f"Unknown target '{args.target}'. "
                f"Supported targets: {', '.join(SUPPORTED_TARGETS)}"
            )
        if config_result:
            config_path, config = config_result
            project_root = config_path.parent
            if args.target in config.get("agents", {}):
                install_path = Path(config["agents"][args.target]["install_path"])
                _do_refresh(project_root, install_path, args.target)
            else:
                install_path = _default_install_path(args.target)
                _do_install(project_root, install_path, args.target, config_path)
        else:
            project_root = Path.cwd()
            install_path = _default_install_path(args.target)
            _do_install(project_root, install_path, args.target, config_path=None)
        return

    # No target: refresh every configured agent.
    if not config_result:
        raise SpexlError(
            "No .spexl.toml found. "
            "Run 'spexl init' to scaffold a project, "
            "then 'spexl install <target>' to install agent assets."
        )

    config_path, config = config_result
    project_root = config_path.parent
    agents = config.get("agents", {})
    if not agents:
        raise SpexlError(
            f"No agents configured in {config_path}. "
            f"Run 'spexl install <target>' to install."
        )
    for target_name, target_config in agents.items():
        install_path = Path(target_config["install_path"])
        _do_refresh(project_root, install_path, target_name)


def _default_install_path(target: str) -> Path:
    if target == "claude":
        return Path(".claude")
    assert False, f"No default install path for target: {target}"


# [AI]
# Context: drop-composition change
# Intent: walk a package resource tree and yield (dest_relative_path, resource) for every file;
#         dest paths are rooted at dest_prefix and mirror the source subtree (e.g. skills/spexl-propose/SKILL.md)
# Assumes: resource is a Traversable exposing iterdir/is_dir/read_text; symlinks not expected
def _walk_resource(
    resource: Traversable,
    dest_prefix: Path,
) -> T.Iterator[tuple[Path, Traversable]]:
    for child in resource.iterdir():
        if child.name.startswith("__") or child.name.startswith("."):
            continue
        child_dest = dest_prefix / child.name
        if child.is_dir():
            yield from _walk_resource(child, child_dest)
        else:
            yield child_dest, child


# [AI]
# Context: drop-composition change
# Intent: enumerate every file to install, keyed by its destination path relative to project root
# Assumes: skills tree under spexl.content.skills, agents under spexl.content.agents
def _managed_files(install_path: Path) -> dict[Path, Traversable]:
    content = importlib.resources.files("spexl.content")
    files: dict[Path, Traversable] = {}
    for dest, resource in _walk_resource(
        content.joinpath("skills"), install_path / "skills"
    ):
        files[dest] = resource
    for dest, resource in _walk_resource(
        content.joinpath("agents"), install_path / "agents"
    ):
        files[dest] = resource
    return files


def _do_install(
    project_root: Path,
    install_path: Path,
    target: str,
    config_path: Path | None,
) -> None:
    files = _managed_files(install_path)
    created = 0
    for rel_path, resource in files.items():
        abs_path = project_root / rel_path
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        abs_path.write_text(resource.read_text(encoding="utf-8"))
        print(f"  created    {_display_path(abs_path)}")
        created += 1

    if config_path:
        update_config(config_path, target, str(install_path))
    else:
        config_path = project_root / CONFIG_FILENAME
        write_config(config_path, agents={target: str(install_path)})
    print(f"  created    {_display_path(config_path)}")

    print(f"\n{created} files created")


def _do_refresh(project_root: Path, install_path: Path, _target: str) -> None:
    files = _managed_files(install_path)
    expected_paths = {project_root / rel for rel in files}
    changed = 0
    unchanged = 0
    removed = 0

    for rel_path, resource in files.items():
        abs_path = project_root / rel_path
        new_content = resource.read_text(encoding="utf-8")
        if abs_path.is_file() and abs_path.read_text() == new_content:
            print(f"  unchanged  {_display_path(abs_path)}")
            unchanged += 1
        else:
            abs_path.parent.mkdir(parents=True, exist_ok=True)
            abs_path.write_text(new_content)
            print(f"  changed    {_display_path(abs_path)}")
            changed += 1

    # [AI]
    # Context: drop-composition change
    # Intent: stale files from a previous install (e.g. skills we've since removed, or old rules/ dir)
    #         should be pruned so the install tree matches the source tree exactly
    # Assumes: only files under managed directories (skills/, agents/) are ours to delete
    for managed_dir in ("skills", "agents"):
        root = project_root / install_path / managed_dir
        if not root.is_dir():
            continue
        for existing in root.rglob("*"):
            if existing.is_file() and existing not in expected_paths:
                existing.unlink()
                print(f"  removed    {_display_path(existing)}")
                removed += 1

    # Also prune the legacy rules/ directory if it exists and only contains the old spexl.md
    legacy_rules = project_root / install_path / "rules" / "spexl.md"
    if legacy_rules.is_file():
        legacy_rules.unlink()
        print(f"  removed    {_display_path(legacy_rules)}")
        removed += 1

    _prune_empty_dirs(project_root / install_path)

    summary = f"\n{changed} files changed, {unchanged} unchanged"
    if removed:
        summary += f", {removed} removed"
    print(summary)


def _do_remove() -> None:
    config_result = _find_existing_config()
    if not config_result:
        print("Nothing to remove")
        return

    config_path, config = config_result
    project_root = config_path.parent
    agents = config.get("agents", {})
    if not agents:
        print("Nothing to remove")
        return

    removed = 0
    for _, target_config in agents.items():
        install_path = Path(target_config["install_path"])
        files = _managed_files(install_path)
        for rel_path in files:
            abs_path = project_root / rel_path
            if abs_path.is_file():
                abs_path.unlink()
                print(f"  removed    {_display_path(abs_path)}")
                removed += 1

        # Legacy rules/ from pre-drop-composition installs
        legacy_rules = project_root / install_path / "rules" / "spexl.md"
        if legacy_rules.is_file():
            legacy_rules.unlink()
            print(f"  removed    {_display_path(legacy_rules)}")
            removed += 1

        _prune_empty_dirs(project_root / install_path)

    # [AI]
    # Context: split-init-install
    # Intent: strip [agents] from .spexl.toml without deleting the file;
    #         project scaffold (.spexl.toml + specs/) is owned by `spexl init`, not install
    _strip_agents(config_path)
    print(f"  updated    {_display_path(config_path)}")

    print(f"\n{removed} files removed")


def _strip_agents(config_path: Path) -> None:
    raw = read_config(config_path) if config_path.stat().st_size > 0 else {}
    raw_loc = raw.get("specs_location", {})
    specs_loc = None
    if raw_loc:
        specs_loc = SpecsLocation(
            dir_path=raw_loc.get("dir_path", "./specs"),
            changes_dir=raw_loc.get("changes_dir", "changes"),
            reference_dir=raw_loc.get("reference_dir", "reference"),
        )
    write_config(config_path, agents=None, specs_location=specs_loc)


def _prune_empty_dirs(root: Path) -> None:
    if not root.is_dir():
        return
    for child in sorted(root.rglob("*"), reverse=True):
        if child.is_dir() and not any(child.iterdir()):
            child.rmdir()
