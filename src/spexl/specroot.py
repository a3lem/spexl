# [AI]
# Context: rewrite-as-spexl (task 1.2)
# Intent: shared helpers used by multiple CLI modules – change resolution,
#         .change.json I/O, status computation
# Note: spec-root discovery moved to spexl.config (ProjectConfig, find_project_root, etc.)

from __future__ import annotations

import json
import re
import string
import typing as T
from pathlib import Path
from random import choices as random_choices

from spexl.errors import SpexlError


def resolve_change(
    changes_dir: Path, identifier: str, include_archived: bool = False
) -> Path:
    """Resolve a change by path, slug, or id."""
    if "/" in identifier:
        p = Path(identifier)
        if p.is_dir():
            return p
        raise SpexlError(f"Path not found: {identifier}")

    direct = changes_dir / identifier
    if direct.is_dir():
        return direct

    if changes_dir.is_dir():
        for d in changes_dir.iterdir():
            if not d.is_dir() or d.name == "archive":
                continue
            cj_path = d / ".change.json"
            if cj_path.is_file():
                data = read_change_json(cj_path)
                if data.get("id") == identifier:
                    return d

    if include_archived:
        archive_dir = changes_dir / "archive"
        if archive_dir.is_dir():
            for d in archive_dir.iterdir():
                if not d.is_dir():
                    continue
                if d.name.endswith(f"-{identifier}"):
                    return d
                cj_path = d / ".change.json"
                if cj_path.is_file():
                    data = read_change_json(cj_path)
                    if data.get("id") == identifier:
                        return d

    hint = (
        " Try --archived to include archived changes."
        if not include_archived
        else ""
    )
    raise SpexlError(f"No change found matching '{identifier}'.{hint}")


def resolve_link(
    spec_root: Path, link: dict[str, str]
) -> tuple[Path, dict[str, T.Any]] | None:
    """Resolve a link to a (change_path, change_json) tuple, or None if broken."""
    target_root = (spec_root / link["specs"]).resolve()
    target_changes = target_root / "changes"
    if not target_changes.is_dir():
        return None
    for d in target_changes.iterdir():
        if not d.is_dir() or d.name == "archive":
            continue
        cj = d / ".change.json"
        if cj.is_file():
            data = read_change_json(cj)
            if data.get("id") == link["change"]:
                return (d, data)
    return None


def compute_status(change_path: Path) -> str:
    """Derive status from artifacts present and task completion.

    The .change.json `skip` field (e.g. ["design", "tasks"]) marks artifacts
    as intentionally omitted. Skipped artifacts are treated as present.
    """
    cj_path = change_path / ".change.json"
    skip: list[str] = []
    if cj_path.is_file():
        data = read_change_json(cj_path)
        raw_skip = data.get("skip")
        if isinstance(raw_skip, list):
            skip = raw_skip

    has_proposal = (change_path / "proposal.md").is_file()
    has_design = (change_path / "design.md").is_file() or "design" in skip
    has_tasks = (change_path / "tasks.md").is_file()
    tasks_skipped = "tasks" in skip

    deltas_dir = change_path / "deltas"
    has_deltas = deltas_dir.is_dir() and any(
        (d / "spec.md").is_file() for d in deltas_dir.iterdir() if d.is_dir()
    )

    all_artifacts = has_proposal and has_design and (has_tasks or tasks_skipped) and has_deltas

    if not all_artifacts:
        return "drafting"

    if tasks_skipped and not has_tasks:
        return "complete"

    text = (change_path / "tasks.md").read_text()
    incomplete = len(re.findall(r"- \[ \]", text))
    complete = len(re.findall(r"- \[x\]", text, re.IGNORECASE))

    if complete == 0:
        return "ready"
    if incomplete > 0:
        return "in progress"
    return "complete"


def read_change_json(path: Path) -> dict[str, T.Any]:
    return json.loads(path.read_text())


def write_change_json(path: Path, data: dict[str, T.Any]) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def generate_id() -> str:
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random_choices(alphabet, k=5))


def count_incomplete_tasks(tasks_path: Path) -> int:
    """Count unchecked checkboxes in tasks.md."""
    text = tasks_path.read_text() if isinstance(tasks_path, Path) else tasks_path
    return len(re.findall(r"- \[ \]", text))


def extract_overview(spec_path: Path) -> str:
    """Extract the first line of the ## Overview section from a reference spec."""
    text = spec_path.read_text()
    in_overview = False
    for line in text.splitlines():
        if line.strip() == "## Overview":
            in_overview = True
            continue
        if in_overview:
            stripped = line.strip()
            if stripped == "":
                continue
            if stripped.startswith("## "):
                break
            return stripped
    return ""


def discover_changes(changes_dir: Path) -> list[dict[str, str]]:
    """List non-archive subdirectories of a changes/ directory."""
    changes = []
    for d in sorted(changes_dir.iterdir()):
        if not d.is_dir() or d.name == "archive":
            continue
        cj_path = d / ".change.json"
        change_id = ""
        if cj_path.is_file():
            data = read_change_json(cj_path)
            change_id = data.get("id", "")
        status = compute_status(d)
        changes.append({"slug": d.name, "id": change_id, "status": status})
    return changes


def discover_archived(archive_dir: Path) -> list[dict[str, str]]:
    """List subdirectories of an archive/ directory."""
    changes = []
    for d in sorted(archive_dir.iterdir()):
        if not d.is_dir():
            continue
        cj_path = d / ".change.json"
        change_id = ""
        reason = ""
        if cj_path.is_file():
            data = read_change_json(cj_path)
            change_id = data.get("id", "")
            archived = data.get("archived", {})
            reason = archived.get("reason", "")
        changes.append({"slug": d.name, "id": change_id, "reason": reason})
    return changes


def parse_sync_summary(spec_path: Path) -> dict[str, int]:
    """Count requirements under each section heading in a spec delta."""
    text = spec_path.read_text()
    counts: dict[str, int] = {}
    current_section: str | None = None

    for line in text.splitlines():
        m = re.match(r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements", line)
        if m:
            current_section = m.group(1).lower()
            counts[current_section] = 0
            continue
        if current_section and re.match(r"^### Requirement:", line):
            counts[current_section] += 1

    return counts


def output(
    data: T.Any,
    formatter: T.Callable[[T.Any], str],
    args: T.Any,
) -> None:
    if getattr(args, "json_output", False):
        print(json.dumps(data, indent=2))
    else:
        print(formatter(data))


def format_change_groups(groups: list[dict[str, T.Any]]) -> str:
    lines = []
    for group in groups:
        lines.append(f"{group['path']}/")
        for c in group["changes"]:
            cid = c.get("id", "")
            status = c.get("status", "") or c.get("reason", "")
            parts = [p for p in [cid, f"[{status}]", c["slug"]] if p]
            lines.append(f"  {' - '.join(parts)}")
    return "\n".join(lines)


def format_info(info: dict[str, T.Any]) -> str:
    lines = []
    id_part = f" ({info['id']})" if info["id"] else ""
    lines.append(f"{info['slug']}{id_part}")
    if info["created"]:
        lines.append(f"created: {info['created']}")
    if info.get("archived"):
        lines.append(f"archived: {info['archived']['reason']}")
    if info["artifacts"]:
        lines.append(f"artifacts: {', '.join(info['artifacts'])}")
    if info["deltas"]:
        lines.append(f"deltas: {', '.join(info['deltas'])}")
    if info["tasks"]["total"]:
        lines.append(
            f"tasks: {info['tasks']['complete']}/{info['tasks']['total']} complete"
        )
    if info.get("links"):
        lines.append("links:")
        for link in info["links"]:
            if link["status"] == "broken":
                lines.append(f"  {link['change']} [broken] ({link['specs']})")
            else:
                lines.append(
                    f"  {link['change']} [{link['status']}] {link['slug']} ({link['specs']})"
                )
    return "\n".join(lines)


def format_refs(refs: list[dict[str, str]]) -> str:
    lines = ["specs/reference/"]
    for r in refs:
        desc = f" - {r['description']}" if r["description"] else ""
        lines.append(f"  {r['name']}{desc}")
    return "\n".join(lines)
