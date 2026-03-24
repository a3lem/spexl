from __future__ import annotations

import argparse
import typing as T
from pathlib import Path

from spexl.cli.changes import relative_display_path
from spexl.config import discover_all_configs, discover_single_config
from spexl.specroot import (
    extract_overview,
    format_ref_groups,
    output,
)


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_refs = subparsers.add_parser("refs", help="List reference specs")
    p_refs.add_argument(
        "--no-recurse",
        action="store_true",
        help="Use only the nearest .spexl.toml (no walk-down)",
    )
    p_refs.add_argument(
        "--long", "-l",
        action="store_true",
        help="Show overview descriptions",
    )
    p_refs.add_argument("--json", action="store_true", dest="json_output")
    p_refs.set_defaults(func=cmd_refs)


def cmd_refs(args: T.Any, start: Path | None = None) -> None:
    no_recurse = getattr(args, "no_recurse", False)

    if no_recurse:
        configs = [discover_single_config(start)]
    else:
        configs = discover_all_configs(start)
        if not configs:
            print("No reference specs")
            return

    base = start or Path.cwd()
    all_groups: list[dict[str, T.Any]] = []
    for cfg in configs:
        ref_dir = cfg.reference_path
        if not ref_dir.is_dir():
            continue
        refs: list[dict[str, str]] = []
        for cap_dir in sorted(ref_dir.iterdir()):
            if not cap_dir.is_dir():
                continue
            spec_file = cap_dir / "spec.md"
            description = ""
            if spec_file.is_file():
                description = extract_overview(spec_file)
            refs.append({"name": cap_dir.name, "description": description})
        if refs:
            display_path = relative_display_path(cfg.project_dir, base)
            all_groups.append({"path": display_path, "refs": refs})

    if not all_groups:
        print("No reference specs")
        return

    long = getattr(args, "long", False)
    output(all_groups, lambda groups: format_ref_groups(groups, long=long), args)
