"""Tests for `spexl changes`.
# spec: cli requirement=changes-archived-filter
# spec: cli requirement=changes-linked-filter
"""

import json
from conftest import run_spexl, make_change, make_archived_change


# spec: spectl requirement=list-active-changes scenario=default
def test_list_changes(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    make_change(spec_root, "fix-sessions", id="p9r4n")
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "x7k2m" in out
    assert "add-oauth" in out
    assert "p9r4n" in out
    assert "fix-sessions" in out


def test_list_changes_json(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("changes", "--json", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    data = json.loads(out)
    assert len(data) == 1
    assert data[0]["changes"][0]["slug"] == "add-oauth"
    assert data[0]["changes"][0]["id"] == "x7k2m"


# spec: cli requirement=recursive-discovery-by-default scenario=multiple-spec-roots
def test_recursive_discovery(spec_root):
    # Create changes in two different spec roots under the same parent
    root1 = spec_root
    make_change(root1, "change-a", id="aaa01")
    sub_dir = spec_root.parent / "sub"
    sub_dir.mkdir(parents=True)
    (sub_dir / ".spexl.toml").write_text("")
    root2 = sub_dir / "specs"
    root2.mkdir()
    (root2 / "changes").mkdir()
    make_change(root2, "change-b", id="bbb01")
    rc, out, err = run_spexl("changes", cwd=spec_root.parent)
    assert rc == 0
    assert "change-a" in out
    assert "change-b" in out


# spec: spectl requirement=list-active-changes scenario=no-changes
def test_no_changes(spec_root):
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "No changes" in out


def test_excludes_archive(spec_root):
    make_change(spec_root, "active-one", id="act01")
    archive = spec_root / "changes" / "archive" / "2026-03-14-old"
    archive.mkdir(parents=True)
    (archive / ".change.json").write_text('{"id": "old01", "created": "2026-03-14"}')
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "old01" not in out
    assert "act01" in out


# spec: spectl requirement=list-active-changes scenario=default
def test_computed_status_in_list(spec_root):
    make_change(spec_root, "drafty", id="dft01")
    make_change(
        spec_root, "in-prog", id="prg01",
        proposal=True, design=True,
        tasks="# Tasks\n- [x] done\n- [ ] todo\n",
        deltas={"auth": "# auth\n## ADDED Requirements\n### Requirement: foo\n"},
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "drafting" in out
    assert "in progress" in out


# spec: cli requirement=changes-archived-filter scenario=all-flag
def test_changes_all(spec_root):
    make_change(spec_root, "active-one", id="act01")
    make_archived_change(
        spec_root, "2026-03-14-old",
        id="arc01", archived={"reason": "merged"},
    )
    rc, out, err = run_spexl("changes", "--all", cwd=spec_root.parent)
    assert rc == 0
    assert "act01" in out
    assert "arc01" in out


# spec: cli requirement=changes-archived-filter scenario=archived-and-all-mutually-exclusive
def test_changes_archived_and_all_exclusive(spec_root):
    rc, out, err = run_spexl("changes", "--archived", "--all", cwd=spec_root.parent)
    assert rc != 0


# spec: cli requirement=changes-linked-filter scenario=filter-to-linked-changes
def test_changes_linked(spec_root):
    make_change(spec_root, "unlinked", id="unl01")
    cp = make_change(spec_root, "linked-one", id="lnk01")
    # Manually add a link
    cj = json.loads((cp / ".change.json").read_text())
    cj["links"] = [{"specs": "../other/specs", "change": "ext01"}]
    (cp / ".change.json").write_text(json.dumps(cj, indent=2) + "\n")

    rc, out, err = run_spexl("changes", "--linked", cwd=spec_root.parent)
    assert rc == 0
    assert "lnk01" in out
    assert "unl01" not in out


# spec: cli requirement=changes-linked-filter scenario=compose-with-archived
def test_changes_linked_archived(spec_root):
    make_archived_change(
        spec_root, "2026-03-14-unlinked",
        id="arc01", archived={"reason": "merged"},
    )
    cp = make_archived_change(
        spec_root, "2026-03-14-linked",
        id="arc02", archived={"reason": "merged"},
    )
    cj = json.loads((cp / ".change.json").read_text())
    cj["links"] = [{"specs": "../other/specs", "change": "ext01"}]
    (cp / ".change.json").write_text(json.dumps(cj, indent=2) + "\n")

    rc, out, err = run_spexl("changes", "--linked", "--archived", cwd=spec_root.parent)
    assert rc == 0
    assert "arc02" in out
    assert "arc01" not in out


# spec: cli requirement=changes-output-formatting
def test_changes_shows_relative_path(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "./" in out
    # Should not contain absolute path or specs/changes/
    assert "specs/changes" not in out


# spec: cli requirement=changes-output-formatting
def test_changes_relative_path_in_monorepo(tmp_path):
    (tmp_path / ".spexl.toml").write_text("")
    for project in ("proj-a", "proj-b"):
        proj_dir = tmp_path / project
        proj_dir.mkdir()
        (proj_dir / ".spexl.toml").write_text("")
        specs = proj_dir / "specs"
        (specs / "changes").mkdir(parents=True)
        (specs / "reference").mkdir()
        make_change(specs, f"{project}-change", id=f"{project}1")

    rc, out, err = run_spexl("changes", cwd=tmp_path)
    assert rc == 0
    assert "./proj-a/" in out or "proj-a" in out
    assert "./proj-b/" in out or "proj-b" in out
    assert str(tmp_path) not in out  # no absolute paths
