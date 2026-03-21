from __future__ import annotations

import argparse
import os
import typing as T
from pathlib import Path

from spexl.errors import SpexlError
from spexl.specroot import read_change_json, write_change_json


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_link = subparsers.add_parser("link", help="Link two changes across spec roots")
    p_link.add_argument("change_a", help="Path to first change directory")
    p_link.add_argument("change_b", help="Path to second change directory")
    p_link.set_defaults(func=cmd_link)

    p_unlink = subparsers.add_parser(
        "unlink", help="Remove link between two changes"
    )
    p_unlink.add_argument("change_a", help="Path to first change directory")
    p_unlink.add_argument("change_b", help="Path to second change directory")
    p_unlink.set_defaults(func=cmd_unlink)


def cmd_link(args: T.Any) -> None:
    path_a = Path(args.change_a)
    path_b = Path(args.change_b)

    if not path_a.is_dir():
        raise SpexlError(f"Path not found: {path_a}")
    if not path_b.is_dir():
        raise SpexlError(f"Path not found: {path_b}")

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"
    if not cj_a_path.is_file():
        raise SpexlError(f"No .change.json in {path_a}")
    if not cj_b_path.is_file():
        raise SpexlError(f"No .change.json in {path_b}")

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


def cmd_unlink(args: T.Any) -> None:
    path_a = Path(args.change_a)
    path_b = Path(args.change_b)

    if not path_a.is_dir():
        raise SpexlError(f"Path not found: {path_a}")
    if not path_b.is_dir():
        raise SpexlError(f"Path not found: {path_b}")

    cj_a_path = path_a / ".change.json"
    cj_b_path = path_b / ".change.json"
    if not cj_a_path.is_file():
        raise SpexlError(f"No .change.json in {path_a}")
    if not cj_b_path.is_file():
        raise SpexlError(f"No .change.json in {path_b}")

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
