#!/usr/bin/env python3
"""spectl -- CLI for mechanical spec management."""

import argparse
import json
import os
import re
import shutil
import string
import sys
from datetime import date
from pathlib import Path
from random import choices as random_choices


# --- main + argument setup ---


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        # link/unlink don't use spec root discovery
        if args.func in (cmd_link, cmd_unlink):
            args.func(args)
        # changes -r handles its own discovery
        elif args.func == cmd_changes and getattr(args, "recursive", False):
            args.func(args, root=None)
        else:
            root = resolve_spec_root(args)
            args.func(args, root)
    except SpectlError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="spectl",
        description="CLI for mechanical spec management",
    )
    parser.add_argument(
        "--dir",
        help="Spec root directory (default: ./specs)",
        metavar="SPEC_DIR",
    )

    subs = parser.add_subparsers(dest="command")

    # new
    p_new = subs.add_parser("new", help="Scaffold a new change")
    p_new.add_argument("slug", help="Change slug (directory name)")
    p_new.set_defaults(func=cmd_new)

    # changes
    p_changes = subs.add_parser("changes", help="List active changes")
    p_changes.add_argument(
        "-r", "--recursive", action="store_true",
        help="Walk down from cwd to find all changes/ directories",
    )
    p_changes.add_argument("--json", action="store_true", dest="json_output")
    p_changes.set_defaults(func=cmd_changes)

    # archived
    p_archived = subs.add_parser("archived", help="List archived changes")
    p_archived.add_argument("--json", action="store_true", dest="json_output")
    p_archived.set_defaults(func=cmd_archived)

    # info
    p_info = subs.add_parser("info", help="Show change overview")
    p_info.add_argument("identifier", help="Change slug, id, or path")
    p_info.add_argument(
        "--archived", action="store_true",
        help="Also search archived changes",
    )
    p_info.add_argument("--json", action="store_true", dest="json_output")
    p_info.set_defaults(func=cmd_info)

    # archive
    p_archive = subs.add_parser("archive", help="Archive a change")
    p_archive.add_argument("identifier", help="Change slug, id, or path")
    p_archive.add_argument(
        "--dry-run", action="store_true",
        help="Print sync summary without moving files",
    )
    p_archive.add_argument(
        "--rejected", action="store_true",
        help="Archive as rejected (skip sync summary)",
    )
    p_archive.add_argument(
        "--force", action="store_true",
        help="Archive even with incomplete tasks",
    )
    p_archive.set_defaults(func=cmd_archive)

    # refs
    p_refs = subs.add_parser("refs", help="List reference specs")
    p_refs.add_argument("--json", action="store_true", dest="json_output")
    p_refs.set_defaults(func=cmd_refs)

    # validate
    p_validate = subs.add_parser("validate", help="Check changes for structural problems")
    p_validate.add_argument(
        "--fix", action="store_true",
        help="Repair fixable issues",
    )
    p_validate.set_defaults(func=cmd_validate)

    # link
    p_link = subs.add_parser("link", help="Link two changes across spec roots")
    p_link.add_argument("change_a", help="Path to first change directory")
    p_link.add_argument("change_b", help="Path to second change directory")
    p_link.set_defaults(func=cmd_link)

    # unlink
    p_unlink = subs.add_parser("unlink", help="Remove link between two changes")
    p_unlink.add_argument("change_a", help="Path to first change directory")
    p_unlink.add_argument("change_b", help="Path to second change directory")
    p_unlink.set_defaults(func=cmd_unlink)

    return parser


# --- commands ---


def cmd_new(args, root):
    changes_dir = root / "changes"
    change_path = changes_dir / args.slug

    if change_path.exists():
        raise SpectlError(
            f"Change '{args.slug}' already exists at {change_path}"
        )

    change_path.mkdir(parents=True)
    (change_path / "deltas").mkdir()

    change_json = {
        "id": generate_id(),
        "created": date.today().isoformat(),
    }
    write_change_json(change_path / ".change.json", change_json)

    print(f"Created {change_path}/ (id: {change_json['id']})")


def cmd_changes(args, root):
    if getattr(args, "recursive", False):
        roots = find_all_spec_roots()
        if not roots:
            print("No active changes")
            return
        all_groups = []
        for r in roots:
            changes_dir = r / "changes"
            if changes_dir.is_dir():
                changes = discover_changes(changes_dir)
                if changes:
                    all_groups.append({
                        "path": str(changes_dir),
                        "changes": changes,
                    })
        if not all_groups:
            print("No active changes")
            return
        output(all_groups, format_change_groups, args)
    else:
        changes_dir = root / "changes"
        if not changes_dir.is_dir():
            print("No active changes")
            return
        changes = discover_changes(changes_dir)
        if not changes:
            print("No active changes")
            return
        group = [{"path": str(changes_dir), "changes": changes}]
        output(group, format_change_groups, args)


def cmd_archived(args, root):
    archive_dir = root / "changes" / "archive"
    if not archive_dir.is_dir():
        print("No archived changes")
        return

    changes = discover_archived(archive_dir)
    if not changes:
        print("No archived changes")
        return

    group = [{"path": str(archive_dir), "changes": changes}]
    output(group, format_change_groups, args)


def cmd_info(args, root):
    changes_dir = root / "changes"
    include_archived = getattr(args, "archived", False)
    change_path = resolve_change(changes_dir, args.identifier, include_archived)
    cj_path = change_path / ".change.json"

    data = read_change_json(cj_path)
    slug = change_path.name
    change_id = data["id"]

    # Compute artifacts present
    artifacts = []
    for name in ("proposal.md", "design.md", "tasks.md"):
        if (change_path / name).is_file():
            artifacts.append(name)

    # Compute deltas
    deltas = []
    deltas_dir = change_path / "deltas"
    if deltas_dir.is_dir():
        for d in sorted(deltas_dir.iterdir()):
            if d.is_dir() and (d / "spec.md").is_file():
                deltas.append(d.name)

    # Task counts
    tasks_total = 0
    tasks_complete = 0
    tasks_path = change_path / "tasks.md"
    if tasks_path.is_file():
        text = tasks_path.read_text()
        tasks_complete = len(re.findall(r"- \[x\]", text, re.IGNORECASE))
        tasks_total = tasks_complete + count_incomplete_tasks(tasks_path)

    # Archived status
    archived = data.get("archived")

    # Resolve links
    resolved_links = []
    raw_links = data.get("links", [])
    if raw_links:
        for link in raw_links:
            result = resolve_link(root, link)
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

    info = {
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


def cmd_archive(args, root):
    changes_dir = root / "changes"
    change_path = resolve_change(changes_dir, args.identifier)

    if args.rejected:
        reason = "rejected"
    else:
        reason = "merged"

        # Check incomplete tasks
        tasks_path = change_path / "tasks.md"
        if tasks_path.is_file():
            incomplete = count_incomplete_tasks(tasks_path)
            if incomplete and not args.force:
                raise SpectlError(
                    f"{incomplete} incomplete tasks remain. Use --force to archive anyway."
                )

        # Sync summary
        deltas_dir = change_path / "deltas"
        summary = []
        if deltas_dir.is_dir():
            for cap_dir in sorted(deltas_dir.iterdir()):
                spec_file = cap_dir / "spec.md"
                if spec_file.is_file():
                    counts = parse_sync_summary(spec_file)
                    is_new = not (root / "reference" / cap_dir.name).is_dir()
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

    # Warn about active linked changes
    cj_path = change_path / ".change.json"
    if cj_path.is_file():
        data = read_change_json(cj_path)
        raw_links = data.get("links", [])
        if raw_links:
            active_warnings = []
            for link in raw_links:
                result = resolve_link(root, link)
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

    # Update .change.json with archived field
    if cj_path.is_file():
        data = read_change_json(cj_path)
        data["archived"] = {"reason": reason}
        write_change_json(cj_path, data)

    # Move to archive
    today = date.today().isoformat()
    archive_dir = changes_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    slug = change_path.name
    dest = archive_dir / f"{today}-{slug}"

    shutil.move(str(change_path), str(dest))
    print(f"Archived to {dest}/")


def cmd_refs(args, root):
    ref_dir = root / "reference"
    if not ref_dir.is_dir():
        print("No reference specs")
        return

    refs = []
    for cap_dir in sorted(ref_dir.iterdir()):
        if not cap_dir.is_dir():
            continue
        spec_file = cap_dir / "spec.md"
        description = ""
        if spec_file.is_file():
            description = extract_overview(spec_file)
        refs.append({"name": cap_dir.name, "description": description})

    if not refs:
        print("No reference specs")
        return

    output(refs, format_refs, args)


def cmd_validate(args, root):
    issues = []
    fixed = []

    # Check active changes
    changes_dir = root / "changes"
    if changes_dir.is_dir():
        for d in sorted(changes_dir.iterdir()):
            if not d.is_dir() or d.name == "archive":
                continue
            validate_change(d, args.fix, issues, fixed, root=root)

    # Check archived changes
    archive_dir = changes_dir / "archive"
    if archive_dir.is_dir():
        for d in sorted(archive_dir.iterdir()):
            if not d.is_dir():
                continue
            validate_change(d, args.fix, issues, fixed, archived=True, root=root)

    if fixed:
        for msg in fixed:
            print(f"fixed: {msg}")

    if issues:
        for msg in issues:
            print(f"error: {msg}", file=sys.stderr)
        sys.exit(1)

    print("All changes valid")


def cmd_link(args):
    path_a = Path(args.change_a)
    path_b = Path(args.change_b)

    if not path_a.is_dir():
        raise SpectlError(f"Path not found: {path_a}")
    if not path_b.is_dir():
        raise SpectlError(f"Path not found: {path_b}")

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"
    if not cj_a_path.is_file():
        raise SpectlError(f"No .change.json in {path_a}")
    if not cj_b_path.is_file():
        raise SpectlError(f"No .change.json in {path_b}")

    data_a = read_change_json(cj_a_path)
    data_b = read_change_json(cj_b_path)
    id_a = data_a["id"]
    id_b = data_b["id"]

    root_a = derive_spec_root(path_a.resolve())
    root_b = derive_spec_root(path_b.resolve())

    rel_a_to_b = os.path.relpath(root_b, root_a)
    rel_b_to_a = os.path.relpath(root_a, root_b)

    # Add link A → B (idempotent)
    links_a = data_a.get("links", [])
    if not any(l["change"] == id_b for l in links_a):
        links_a.append({"specs": rel_a_to_b, "change": id_b})
        data_a["links"] = links_a
        write_change_json(cj_a_path, data_a)

    # Add link B → A (idempotent)
    links_b = data_b.get("links", [])
    if not any(l["change"] == id_a for l in links_b):
        links_b.append({"specs": rel_b_to_a, "change": id_a})
        data_b["links"] = links_b
        write_change_json(cj_b_path, data_b)

    print(f"Linked {path_a.name} <-> {path_b.name}")


def cmd_unlink(args):
    path_a = Path(args.change_a)
    path_b = Path(args.change_b)

    if not path_a.is_dir():
        raise SpectlError(f"Path not found: {path_a}")
    if not path_b.is_dir():
        raise SpectlError(f"Path not found: {path_b}")

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"
    if not cj_a_path.is_file():
        raise SpectlError(f"No .change.json in {path_a}")
    if not cj_b_path.is_file():
        raise SpectlError(f"No .change.json in {path_b}")

    data_a = read_change_json(cj_a_path)
    data_b = read_change_json(cj_b_path)
    id_a = data_a["id"]
    id_b = data_b["id"]

    # Remove link A → B
    links_a = data_a.get("links", [])
    links_a = [l for l in links_a if l["change"] != id_b]
    if links_a:
        data_a["links"] = links_a
    else:
        data_a.pop("links", None)
    write_change_json(cj_a_path, data_a)

    # Remove link B → A
    links_b = data_b.get("links", [])
    links_b = [l for l in links_b if l["change"] != id_a]
    if links_b:
        data_b["links"] = links_b
    else:
        data_b.pop("links", None)
    write_change_json(cj_b_path, data_b)

    print(f"Unlinked {path_a.name} <-> {path_b.name}")


# --- helpers ---


class SpectlError(Exception):
    pass


def derive_spec_root(change_path):
    """Derive the spec root from a change directory path.

    Expects: .../specs/changes/slug/ -> returns .../specs/
    """
    return change_path.parent.parent


def resolve_link(spec_root, link):
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


def resolve_spec_root(args):
    if getattr(args, "dir", None):
        root = Path(args.dir)
        if not root.is_dir():
            raise SpectlError(f"Directory not found: {root}")
        return root
    root = Path("specs")
    if not root.is_dir():
        raise SpectlError("No specs/ directory found. Use --dir to specify.")
    return root


def find_all_spec_roots():
    """Walk down from cwd to find directories that contain a changes/ subdir."""
    roots = []
    for p in sorted(Path(".").rglob("changes")):
        if p.is_dir() and p.parent not in roots:
            if "archive" in p.parts:
                continue
            roots.append(p.parent)
    return roots


def discover_changes(changes_dir):
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


def discover_archived(archive_dir):
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


def resolve_change(changes_dir, identifier, include_archived=False):
    """Resolve a change by path, slug, or id."""
    # If identifier contains /, treat as path
    if "/" in identifier:
        p = Path(identifier)
        if p.is_dir():
            return p
        raise SpectlError(f"Path not found: {identifier}")

    # Try slug first (direct directory match)
    direct = changes_dir / identifier
    if direct.is_dir():
        return direct

    # Scan active changes for matching id
    if changes_dir.is_dir():
        for d in changes_dir.iterdir():
            if not d.is_dir() or d.name == "archive":
                continue
            cj_path = d / ".change.json"
            if cj_path.is_file():
                data = read_change_json(cj_path)
                if data.get("id") == identifier:
                    return d

    # Scan archive if requested
    if include_archived:
        archive_dir = changes_dir / "archive"
        if archive_dir.is_dir():
            for d in archive_dir.iterdir():
                if not d.is_dir():
                    continue
                # Check if slug appears in the directory name (archive dirs are date-prefixed)
                if d.name.endswith(f"-{identifier}"):
                    return d
                cj_path = d / ".change.json"
                if cj_path.is_file():
                    data = read_change_json(cj_path)
                    if data.get("id") == identifier:
                        return d

    hint = " Try --archived to include archived changes." if not include_archived else ""
    raise SpectlError(
        f"No change found matching '{identifier}'.{hint}"
    )


def compute_status(change_path):
    """Derive status from artifacts present and task completion."""
    has_proposal = (change_path / "proposal.md").is_file()
    has_design = (change_path / "design.md").is_file()
    has_tasks = (change_path / "tasks.md").is_file()

    deltas_dir = change_path / "deltas"
    has_deltas = deltas_dir.is_dir() and any(
        (d / "spec.md").is_file()
        for d in deltas_dir.iterdir()
        if d.is_dir()
    )

    all_artifacts = has_proposal and has_design and has_tasks and has_deltas

    if not all_artifacts:
        return "drafting"

    # All artifacts present -- check task progress
    text = (change_path / "tasks.md").read_text()
    incomplete = len(re.findall(r"- \[ \]", text))
    complete = len(re.findall(r"- \[x\]", text, re.IGNORECASE))

    if complete == 0:
        return "ready"
    if incomplete > 0:
        return "in progress"
    return "complete"


def validate_change(change_path, fix, issues, fixed, archived=False, root=None):
    """Check a single change for structural problems."""
    name = change_path.name
    cj_path = change_path / ".change.json"

    if not cj_path.is_file():
        issues.append(f"{name}: missing .change.json")
        return

    data = read_change_json(cj_path)
    dirty = False

    # Missing id
    if "id" not in data:
        if fix:
            data["id"] = generate_id()
            dirty = True
            fixed.append(f"{name}: generated id '{data['id']}'")
        else:
            issues.append(f"{name}: .change.json missing 'id'")

    # Missing created
    if "created" not in data:
        if fix:
            data["created"] = date.today().isoformat()
            dirty = True
            fixed.append(f"{name}: set created to {data['created']}")
        else:
            issues.append(f"{name}: .change.json missing 'created'")

    # Archived merged change with open tasks
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

    # Check link integrity (active changes only)
    if not archived and root and "id" in data:
        for link in data.get("links", []):
            result = resolve_link(root, link)
            if result is None:
                issues.append(
                    f"{name}: broken link to change '{link['change']}' "
                    f"via specs path '{link['specs']}'"
                )
            else:
                # Check back-link
                target_path, target_data = result
                target_links = target_data.get("links", [])
                has_backlink = any(
                    l["change"] == data["id"] for l in target_links
                )
                if not has_backlink:
                    if fix:
                        target_root = (root / link["specs"]).resolve()
                        rev_path = os.path.relpath(root.resolve(), target_root)
                        target_links.append({
                            "specs": rev_path,
                            "change": data["id"],
                        })
                        target_data["links"] = target_links
                        write_change_json(target_path / ".change.json", target_data)
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


def extract_overview(spec_path):
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


def read_change_json(path):
    return json.loads(path.read_text())


def write_change_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def generate_id():
    alphabet = string.ascii_lowercase + string.digits
    return "".join(random_choices(alphabet, k=5))


def parse_sync_summary(spec_path):
    """Count requirements under each section heading in a spec delta."""
    text = spec_path.read_text()
    counts = {}
    current_section = None

    for line in text.splitlines():
        m = re.match(r"^## (ADDED|MODIFIED|REMOVED|RENAMED) Requirements", line)
        if m:
            current_section = m.group(1).lower()
            counts[current_section] = 0
            continue
        if current_section and re.match(r"^### Requirement:", line):
            counts[current_section] += 1

    return counts


def count_incomplete_tasks(tasks_path):
    """Count unchecked checkboxes in tasks.md."""
    text = tasks_path.read_text() if isinstance(tasks_path, Path) else tasks_path
    return len(re.findall(r"- \[ \]", text))


def output(data, formatter, args):
    if getattr(args, "json_output", False):
        print(json.dumps(data, indent=2))
    else:
        print(formatter(data))


def format_change_groups(groups):
    lines = []
    for group in groups:
        lines.append(f"{group['path']}/")
        for c in group["changes"]:
            cid = c.get("id", "")
            status = c.get("status", "") or c.get("reason", "")
            parts = [p for p in [cid, f"[{status}]", c["slug"]] if p]
            lines.append(f"  {' - '.join(parts)}")
    return "\n".join(lines)


def format_info(info):
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
        lines.append(f"tasks: {info['tasks']['complete']}/{info['tasks']['total']} complete")
    if info.get("links"):
        lines.append("links:")
        for link in info["links"]:
            if link["status"] == "broken":
                lines.append(f"  {link['change']} [broken] ({link['specs']})")
            else:
                lines.append(f"  {link['change']} [{link['status']}] {link['slug']} ({link['specs']})")
    return "\n".join(lines)


def format_refs(refs):
    lines = ["specs/reference/"]
    for r in refs:
        desc = f" - {r['description']}" if r["description"] else ""
        lines.append(f"  {r['name']}{desc}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
