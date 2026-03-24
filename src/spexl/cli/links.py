from __future__ import annotations

import argparse
import os
import typing as T
from pathlib import Path

from spexl.config import ProjectConfig, discover_all_configs, discover_single_config
from spexl.errors import SpexlError
from spexl.specroot import read_change_json, resolve_change, write_change_json


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_link = subparsers.add_parser("link", help="Link two changes across spec roots")
    p_link.add_argument("change_a", help="Change slug, id, or path")
    p_link.add_argument("change_b", help="Change slug, id, or path")
    p_link.set_defaults(func=cmd_link)

    p_unlink = subparsers.add_parser(
        "unlink", help="Remove link between two changes"
    )
    p_unlink.add_argument("change_a", help="Change slug, id, or path")
    p_unlink.add_argument("change_b", help="Change slug, id, or path")
    p_unlink.set_defaults(func=cmd_unlink)


def _resolve_change_identifier(
    identifier: str, start: Path | None
) -> tuple[Path, ProjectConfig]:
    """Resolve a change identifier (path, slug, or id) across all configs."""
    configs = discover_all_configs(start)
    if not configs:
        configs = [discover_single_config(start)]

    for cfg in configs:
        try:
            change_path = resolve_change(cfg.changes_path, identifier)
            return change_path, cfg
        except SpexlError:
            continue

    raise SpexlError(f"Change not found: '{identifier}'.")


def cmd_link(args: T.Any, start: Path | None = None) -> None:
    path_a, _ = _resolve_change_identifier(args.change_a, start)
    path_b, _ = _resolve_change_identifier(args.change_b, start)

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"

    data_a = read_change_json(cj_a_path)
    data_b = read_change_json(cj_b_path)
    id_a = data_a["id"]
    id_b = data_b["id"]

    # Derive spec root: change_path is .../specs/changes/slug/
    root_a = path_a.resolve().parent.parent
    root_b = path_b.resolve().parent.parent

    rel_a_to_b = os.path.relpath(root_b, root_a)
    rel_b_to_a = os.path.relpath(root_a, root_b)

    links_a = data_a.get("links", [])
    if not any(link["change"] == id_b for link in links_a):
        links_a.append({"specs": rel_a_to_b, "change": id_b})
        data_a["links"] = links_a
        write_change_json(cj_a_path, data_a)

    links_b = data_b.get("links", [])
    if not any(link["change"] == id_a for link in links_b):
        links_b.append({"specs": rel_b_to_a, "change": id_a})
        data_b["links"] = links_b
        write_change_json(cj_b_path, data_b)

    print(f"Linked {path_a.name} <-> {path_b.name}")


def cmd_unlink(args: T.Any, start: Path | None = None) -> None:
    path_a, _ = _resolve_change_identifier(args.change_a, start)
    path_b, _ = _resolve_change_identifier(args.change_b, start)

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"

    data_a = read_change_json(cj_a_path)
    data_b = read_change_json(cj_b_path)
    id_a = data_a["id"]
    id_b = data_b["id"]

    links_a = data_a.get("links", [])
    links_a = [link for link in links_a if link["change"] != id_b]
    if links_a:
        data_a["links"] = links_a
    else:
        data_a.pop("links", None)
    write_change_json(cj_a_path, data_a)

    links_b = data_b.get("links", [])
    links_b = [link for link in links_b if link["change"] != id_a]
    if links_b:
        data_b["links"] = links_b
    else:
        data_b.pop("links", None)
    write_change_json(cj_b_path, data_b)

    print(f"Unlinked {path_a.name} <-> {path_b.name}")
