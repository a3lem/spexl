from __future__ import annotations

import argparse
import os
import re
import shutil
import typing as T
from datetime import date
from pathlib import Path

from spexl.config import (
    ProjectConfig,
    discover_all_configs,
    discover_single_config,
)
from spexl.errors import SpexlError
from spexl.specroot import (
    compute_status,
    count_incomplete_tasks,
    discover_archived,
    discover_changes,
    format_change_groups,
    format_info,
    generate_id,
    output,
    parse_sync_summary,
    read_change_json,
    resolve_change,
    resolve_link,
    write_change_json,
)


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_new = subparsers.add_parser("new", help="Scaffold a new change")
    p_new.add_argument("slug", help="Change slug (directory name)")
    p_new.add_argument(
        "--skip",
        action="append",
        dest="skip",
        help="Artifact to skip in status computation (design, tasks). Repeatable.",
    )
    p_new.set_defaults(func=cmd_new)

    p_changes = subparsers.add_parser("changes", help="List changes")
    p_changes.add_argument(
        "--no-recurse",
        action="store_true",
        help="Use only the nearest .spexl.toml (no walk-down)",
    )
    scope = p_changes.add_mutually_exclusive_group()
    scope.add_argument(
        "--archived",
        action="store_true",
        help="Show only archived changes",
    )
    scope.add_argument(
        "--all",
        action="store_true",
        dest="show_all",
        help="Show both active and archived changes",
    )
    p_changes.add_argument(
        "--linked",
        action="store_true",
        help="Show only changes with cross-project links",
    )
    p_changes.add_argument("--json", action="store_true", dest="json_output")
    p_changes.set_defaults(func=cmd_changes)

    p_info = subparsers.add_parser("info", help="Show change overview")
    p_info.add_argument("identifier", help="Change slug, id, or path")
    p_info.add_argument(
        "--archived",
        action="store_true",
        help="Also search archived changes",
    )
    p_info.add_argument("--json", action="store_true", dest="json_output")
    p_info.set_defaults(func=cmd_info)

    p_archive = subparsers.add_parser("archive", help="Archive a change")
    p_archive.add_argument("identifier", help="Change slug, id, or path")
    p_archive.add_argument(
        "--dry-run",
        action="store_true",
        help="Print sync summary without moving files",
    )
    p_archive.add_argument(
        "--rejected",
        action="store_true",
        help="Archive as rejected (skip sync summary)",
    )
    p_archive.add_argument(
        "--force",
        action="store_true",
        help="Archive even with incomplete tasks",
    )
    p_archive.set_defaults(func=cmd_archive)


def cmd_new(args: T.Any, config: ProjectConfig) -> None:
    changes_dir = config.changes_path
    change_path = changes_dir / args.slug

    if change_path.exists():
        raise SpexlError(
            f"Change '{args.slug}' already exists at {change_path}"
        )

    change_path.mkdir(parents=True)
    (change_path / "deltas").mkdir()

    change_json: dict[str, str | list[str]] = {
        "id": generate_id(),
        "created": date.today().isoformat(),
    }

    if args.skip:
        valid_skip = {"design", "tasks"}
        invalid = set(args.skip) - valid_skip
        if invalid:
            raise SpexlError(
                f"Invalid --skip values: {', '.join(sorted(invalid))}. "
                f"Valid: {', '.join(sorted(valid_skip))}"
            )
        change_json["skip"] = sorted(set(args.skip))

    write_change_json(change_path / ".change.json", change_json)

    print(f"Created {change_path}/ (id: {change_json['id']})")


def cmd_changes(args: T.Any, start: Path | None = None) -> None:
    show_archived = getattr(args, "archived", False)
    show_all = getattr(args, "show_all", False)
    linked_only = getattr(args, "linked", False)
    no_recurse = getattr(args, "no_recurse", False)

    if no_recurse:
        configs = [discover_single_config(start)]
    else:
        configs = discover_all_configs(start)
        if not configs:
            print("No changes")
            return

    all_groups: list[dict[str, T.Any]] = []
    for cfg in configs:
        changes_dir = cfg.changes_path

        if not show_archived:
            if changes_dir.is_dir():
                active = discover_changes(changes_dir)
                if linked_only:
                    active = _filter_linked(changes_dir, active)
                if active:
                    all_groups.append({"path": str(changes_dir), "changes": active})

        if show_archived or show_all:
            archive_dir = changes_dir / "archive"
            if archive_dir.is_dir():
                archived = discover_archived(archive_dir)
                if linked_only:
                    archived = _filter_linked(archive_dir, archived)
                if archived:
                    all_groups.append({"path": str(archive_dir), "changes": archived})

    if not all_groups:
        print("No changes")
        return
    output(all_groups, format_change_groups, args)


def _filter_linked(
    base_dir: Path, changes: list[dict[str, str]]
) -> list[dict[str, str]]:
    """Keep only changes whose .change.json has a non-empty links array."""
    result = []
    for c in changes:
        cj_path = base_dir / c["slug"] / ".change.json"
        if cj_path.is_file():
            data = read_change_json(cj_path)
            if data.get("links"):
                result.append(c)
    return result


def _resolve_across_configs(
    identifier: str,
    start: Path | None,
    include_archived: bool = False,
) -> tuple[Path, ProjectConfig]:
    """Resolve a change identifier across all discovered configs.

    Returns (change_path, matched_config).
    """
    configs = discover_all_configs(start)
    if not configs:
        configs = [discover_single_config(start)]

    for cfg in configs:
        try:
            change_path = resolve_change(
                cfg.changes_path, identifier, include_archived
            )
            return change_path, cfg
        except SpexlError:
            continue

    hint = (
        " Try --archived to include archived changes."
        if not include_archived
        else ""
    )
    raise SpexlError(f"No change found matching '{identifier}'.{hint}")


def cmd_info(args: T.Any, start: Path | None = None) -> None:
    include_archived = getattr(args, "archived", False)
    change_path, matched_config = _resolve_across_configs(
        args.identifier, start, include_archived
    )

    cj_path = change_path / ".change.json"

    data = read_change_json(cj_path)
    slug = change_path.name
    change_id = data["id"]

    artifacts = []
    for name in ("proposal.md", "design.md", "tasks.md"):
        if (change_path / name).is_file():
            artifacts.append(name)

    deltas: list[str] = []
    deltas_dir = change_path / "deltas"
    if deltas_dir.is_dir():
        for d in sorted(deltas_dir.iterdir()):
            if d.is_dir() and (d / "spec.md").is_file():
                deltas.append(d.name)

    tasks_total = 0
    tasks_complete = 0
    tasks_path = change_path / "tasks.md"
    if tasks_path.is_file():
        text = tasks_path.read_text()
        tasks_complete = len(re.findall(r"- \[x\]", text, re.IGNORECASE))
        tasks_total = tasks_complete + count_incomplete_tasks(tasks_path)

    archived = data.get("archived")

    resolved_links: list[dict[str, T.Any]] = []
    raw_links = data.get("links", [])
    if raw_links:
        for link in raw_links:
            result = resolve_link(matched_config.specs_dir, link)
            if result:
                target_path, target_data = result
                resolved_links.append({
                    "specs": link["specs"],
                    "change": link["change"],
                    "slug": target_path.name,
                    "status": compute_status(target_path),
                })
            else:
                resolved_links.append({
                    "specs": link["specs"],
                    "change": link["change"],
                    "status": "broken",
                })

    info: dict[str, T.Any] = {
        "slug": slug,
        "id": change_id,
        "created": data.get("created", ""),
        "artifacts": artifacts,
        "deltas": deltas,
        "tasks": {"complete": tasks_complete, "total": tasks_total},
    }
    if archived:
        info["archived"] = archived
    if resolved_links:
        info["links"] = resolved_links

    output(info, format_info, args)


def cmd_archive(args: T.Any, start: Path | None = None) -> None:
    change_path, config = _resolve_across_configs(args.identifier, start)
    changes_dir = config.changes_path

    if args.rejected:
        reason = "rejected"
    else:
        reason = "merged"

        tasks_path = change_path / "tasks.md"
        if tasks_path.is_file():
            incomplete = count_incomplete_tasks(tasks_path)
            if incomplete and not args.force:
                raise SpexlError(
                    f"{incomplete} incomplete tasks remain. Use --force to archive anyway."
                )

        deltas_dir = change_path / "deltas"
        summary: list[dict[str, T.Any]] = []
        if deltas_dir.is_dir():
            for cap_dir in sorted(deltas_dir.iterdir()):
                spec_file = cap_dir / "spec.md"
                if spec_file.is_file():
                    counts = parse_sync_summary(spec_file)
                    is_new = not (config.reference_path / cap_dir.name).is_dir()
                    summary.append({
                        "capability": cap_dir.name,
                        "new": is_new,
                        **counts,
                    })

        if summary:
            print("Sync summary:")
            for s in summary:
                parts = []
                for section in ("added", "modified", "removed", "renamed"):
                    n = s.get(section, 0)
                    if n:
                        unit = "requirement" if n == 1 else "requirements"
                        parts.append(f"{n} {section} {unit}")
                label = ", ".join(parts) if parts else "no changes"
                if s["new"]:
                    print(f"  {s['capability']}: NEW capability ({label})")
                else:
                    print(f"  {s['capability']}: {label}")

    cj_path = change_path / ".change.json"
    if cj_path.is_file():
        data = read_change_json(cj_path)
        raw_links = data.get("links", [])
        if raw_links:
            active_warnings = []
            for link in raw_links:
                result = resolve_link(config.specs_dir, link)
                if result:
                    target_path, _ = result
                    status = compute_status(target_path)
                    active_warnings.append(
                        f"  {link['change']} [{status}] {target_path.name} ({link['specs']})"
                    )
                else:
                    active_warnings.append(
                        f"  {link['change']} [broken] ({link['specs']})"
                    )
            if active_warnings:
                print("Linked changes still active:")
                for w in active_warnings:
                    print(w)

    if args.dry_run:
        return

    if cj_path.is_file():
        data = read_change_json(cj_path)
        data["archived"] = {"reason": reason}
        write_change_json(cj_path, data)

    today = date.today().isoformat()
    archive_dir = changes_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    slug = change_path.name
    dest = archive_dir / f"{today}-{slug}"

    shutil.move(str(change_path), str(dest))
    print(f"Archived to {dest}/")
