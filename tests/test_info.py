"""Tests for `spectl info`.
# spec: spectl requirement=change-info
"""

import json
from conftest import run_spexl, make_change, make_archived_change


# spec: spectl requirement=change-info scenario=info-output
def test_info_output(spec_root):
    make_change(
        spec_root, "add-oauth", id="x7k2m", created="2026-03-14",
        proposal=True, design=True,
        tasks="# Tasks\n- [x] one\n- [x] two\n- [x] three\n- [ ] four\n- [ ] five\n",
        deltas={"user-auth": "# user-auth\n## ADDED Requirements\n"},
    )
    rc, out, err = run_spexl("info", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth (x7k2m)" in out
    assert "created: 2026-03-14" in out
    assert "artifacts: proposal.md, design.md, tasks.md" in out
    assert "deltas: user-auth" in out
    assert "tasks: 3/5 complete" in out


# spec: spectl requirement=change-info scenario=info-with-json
def test_info_json(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m", proposal=True)
    rc, out, err = run_spexl("info", "add-oauth", "--json", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    data = json.loads(out)
    assert data["slug"] == "add-oauth"
    assert data["id"] == "x7k2m"
    assert "proposal.md" in data["artifacts"]


# spec: spectl requirement=change-info scenario=resolve-by-slug-or-id-active
def test_info_resolve_by_id(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("info", "x7k2m", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth" in out


# spec: spectl requirement=change-info scenario=resolve-by-path
def test_info_resolve_by_path(spec_root):
    cp = make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("info", str(cp), "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth" in out


# spec: spectl requirement=change-info scenario=resolve-by-slug-or-id-archived
def test_info_archived_by_slug(spec_root):
    make_archived_change(
        spec_root, "2026-03-14-add-oauth",
        id="x7k2m", archived={"reason": "merged"},
    )
    rc, out, err = run_spexl(
        "info", "add-oauth", "--archived", "--cwd", str(spec_root.parent),
        cwd=spec_root.parent,
    )
    assert rc == 0
    assert "archived: merged" in out


# spec: spectl requirement=change-info scenario=resolve-by-slug-or-id-archived
def test_info_archived_by_id(spec_root):
    make_archived_change(
        spec_root, "2026-03-14-add-oauth",
        id="x7k2m", archived={"reason": "merged"},
    )
    rc, out, err = run_spexl(
        "info", "x7k2m", "--archived", "--cwd", str(spec_root.parent),
        cwd=spec_root.parent,
    )
    assert rc == 0
    assert "archived: merged" in out


# spec: spectl requirement=change-info scenario=info-for-archived-change
def test_info_archived_by_path(spec_root):
    cp = make_archived_change(
        spec_root, "2026-03-14-add-oauth",
        id="x7k2m", archived={"reason": "merged"},
    )
    rc, out, err = run_spexl("info", str(cp), "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "archived: merged" in out


# spec: spectl requirement=change-info scenario=no-match
def test_info_no_match(spec_root):
    rc, out, err = run_spexl("info", "nonexistent", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "No change found" in err


def test_info_no_match_hints_archived(spec_root):
    rc, out, err = run_spexl("info", "nonexistent", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "--archived" in err


def test_info_finds_change_in_sub_project(tmp_path):
    """info should find changes in sub-project spec roots, not just the nearest one."""
    # Root project
    root = tmp_path
    (root / ".spexl.toml").write_text("")
    root_specs = root / "specs"
    root_specs.mkdir()
    (root_specs / "changes").mkdir()
    (root_specs / "reference").mkdir()

    # Sub-project with its own .spexl.toml
    sub = root / "sub"
    sub.mkdir()
    (sub / ".spexl.toml").write_text("")
    sub_specs = sub / "specs"
    sub_specs.mkdir()
    (sub_specs / "changes").mkdir()
    (sub_specs / "reference").mkdir()

    make_change(sub_specs, "sub-feature", id="sub01", proposal=True)

    # Run info from the root – should find the sub-project's change
    rc, out, err = run_spexl("info", "sub-feature", "--cwd", str(root), cwd=root)
    assert rc == 0
    assert "sub-feature (sub01)" in out

    # Also resolve by id
    rc, out, err = run_spexl("info", "sub01", "--cwd", str(root), cwd=root)
    assert rc == 0
    assert "sub-feature" in out
