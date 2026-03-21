from __future__ import annotations

import argparse
import os
import sys
import typing as T
from datetime import date
from pathlib import Path

from spexl.config import discover_all_configs, discover_single_config
from spexl.specroot import (
    count_incomplete_tasks,
    generate_id,
    read_change_json,
    resolve_link,
    write_change_json,
)


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_validate = subparsers.add_parser(
        "validate", help="Check changes for structural problems"
    )
    p_validate.add_argument(
        "--fix",
        action="store_true",
        help="Repair fixable issues",
    )
    p_validate.add_argument(
        "--no-recurse",
        action="store_true",
        help="Use only the nearest .spexl.toml (no walk-down)",
    )
    p_validate.set_defaults(func=cmd_validate)


def cmd_validate(args: T.Any, start: Path | None = None) -> None:
    no_recurse = getattr(args, "no_recurse", False)

    if no_recurse:
        configs = [discover_single_config(start)]
    else:
        configs = discover_all_configs(start)
        if not configs:
            print("All changes valid")
            return

    issues: list[str] = []
    fixed: list[str] = []

    for cfg in configs:
        changes_dir = cfg.changes_path
        specs_dir = cfg.specs_dir
        if changes_dir.is_dir():
            for d in sorted(changes_dir.iterdir()):
                if not d.is_dir() or d.name == "archive":
                    continue
                validate_change(d, args.fix, issues, fixed, specs_dir=specs_dir)

        archive_dir = changes_dir / "archive"
        if archive_dir.is_dir():
            for d in sorted(archive_dir.iterdir()):
                if not d.is_dir():
                    continue
                validate_change(d, args.fix, issues, fixed, archived=True, specs_dir=specs_dir)

    if fixed:
        for msg in fixed:
            print(f"fixed: {msg}")

    if issues:
        for msg in issues:
            print(f"error: {msg}", file=sys.stderr)
        sys.exit(1)

    print("All changes valid")


def validate_change(
    change_path: Path,
    fix: bool,
    issues: list[str],
    fixed: list[str],
    archived: bool = False,
    specs_dir: Path | None = None,
) -> None:
    """Check a single change for structural problems."""
    name = change_path.name
    cj_path = change_path / ".change.json"

    if not cj_path.is_file():
        issues.append(f"{name}: missing .change.json")
        return

    data = read_change_json(cj_path)
    dirty = False

    if "id" not in data:
        if fix:
            data["id"] = generate_id()
            dirty = True
            fixed.append(f"{name}: generated id '{data['id']}'")
        else:
            issues.append(f"{name}: .change.json missing 'id'")

    if "created" not in data:
        if fix:
            data["created"] = date.today().isoformat()
            dirty = True
            fixed.append(f"{name}: set created to {data['created']}")
        else:
            issues.append(f"{name}: .change.json missing 'created'")

    skip = data.get("skip")
    if skip is not None:
        valid_skip = {"design", "tasks"}
        if not isinstance(skip, list):
            issues.append(f"{name}: .change.json 'skip' must be a list")
        else:
            invalid = set(skip) - valid_skip
            if invalid:
                issues.append(
                    f"{name}: .change.json invalid skip values: "
                    f"{', '.join(sorted(invalid))}. Valid: {', '.join(sorted(valid_skip))}"
                )

    if archived:
        arch = data.get("archived", {})
        if arch.get("reason") == "merged":
            tasks_path = change_path / "tasks.md"
            if tasks_path.is_file():
                incomplete = count_incomplete_tasks(tasks_path)
                if incomplete:
                    issues.append(
                        f"{name}: archived as merged but has {incomplete} open tasks"
                    )

    if not archived and specs_dir and "id" in data:
        for link in data.get("links", []):
            result = resolve_link(specs_dir, link)
            if result is None:
                issues.append(
                    f"{name}: broken link to change '{link['change']}' "
                    f"via specs path '{link['specs']}'"
                )
            else:
                target_path, target_data = result
                target_links = target_data.get("links", [])
                has_backlink = any(
                    l_entry["change"] == data["id"] for l_entry in target_links
                )
                if not has_backlink:
                    if fix:
                        target_root = (specs_dir / link["specs"]).resolve()
                        rev_path = os.path.relpath(specs_dir.resolve(), target_root)
                        target_links.append({
                            "specs": rev_path,
                            "change": data["id"],
                        })
                        target_data["links"] = target_links
                        write_change_json(
                            target_path / ".change.json", target_data
                        )
                        fixed.append(
                            f"{target_path.name}: added back-link to {name}"
                        )
                    else:
                        issues.append(
                            f"{name}: asymmetric link to '{link['change']}' "
                            f"({target_path.name} does not link back)"
                        )

    if dirty:
        write_change_json(cj_path, data)
