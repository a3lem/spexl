# [AI]
# Context: spex-9c9a (shablon migration); spexl install + steering removed.
# Intent: project scaffolding only -- write .spexl.toml + specs/{changes,reference}/

from __future__ import annotations

import argparse
import os
import sys
import typing as T
from pathlib import Path

from spexl.config import (
    CONFIG_FILENAME,
    ProjectConfig,
    SpecsLocation,
    write_config,
)
from spexl.errors import SpexlError


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_init = subparsers.add_parser(
        "init", help="Scaffold a spexl project (.spexl.toml + specs/)"
    )
    p_init.add_argument("target", nargs="?", help=argparse.SUPPRESS)
    p_init.set_defaults(func=cmd_init)


def _display_path(abs_path: Path) -> str:
    return os.path.relpath(abs_path.resolve(), Path.cwd().resolve())


def cmd_init(args: T.Any) -> None:
    if args.target:
        raise SpexlError(
            "'spexl init' takes no arguments. "
            "Skills and subagents are distributed via the spexl Claude Code plugin -- "
            "install through your agent's plugin mechanism, not the CLI."
        )

    cwd = Path.cwd()
    local_config = cwd / CONFIG_FILENAME

    if local_config.is_file():
        cfg = ProjectConfig.from_toml(local_config)
        if cfg.specs_dir.is_dir():
            print("spexl already initialized in this directory", file=sys.stderr)
            return

    config_existed = local_config.is_file()
    if not config_existed:
        write_config(local_config)
        print(f"  created    {_display_path(local_config)}")

    specs_loc = SpecsLocation()
    specs_dir = cwd / specs_loc.dir_path
    for sub in (specs_loc.changes_dir, specs_loc.reference_dir):
        d = specs_dir / sub
        if not d.is_dir():
            d.mkdir(parents=True, exist_ok=True)
            print(f"  created    {_display_path(d)}/")

    if not config_existed:
        print("\nProject initialized.")

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
