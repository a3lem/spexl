"""Tests for `spectl validate`.
# spec: spectl requirement=validate-changes
"""

import json
from conftest import run_spexl, make_change, make_archived_change


# spec: spectl requirement=validate-changes scenario=missing-id
def test_validate_missing_id(spec_root):
    cp = make_change(spec_root, "bad-change", id="tmp01")
    cj = json.loads((cp / ".change.json").read_text())
    del cj["id"]
    (cp / ".change.json").write_text(json.dumps(cj))
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "missing 'id'" in err


# spec: spectl requirement=validate-changes scenario=fix-missing-id
def test_validate_fix_missing_id(spec_root):
    cp = make_change(spec_root, "bad-change", id="tmp01")
    cj = json.loads((cp / ".change.json").read_text())
    del cj["id"]
    (cp / ".change.json").write_text(json.dumps(cj))
    rc, out, err = run_spexl("validate", "--fix", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "generated id" in out

    # Verify it was written
    cj = json.loads((cp / ".change.json").read_text())
    assert "id" in cj
    assert len(cj["id"]) == 5


# spec: spectl requirement=validate-changes scenario=missing-created-date
def test_validate_missing_created(spec_root):
    cp = make_change(spec_root, "bad-change", id="tmp01")
    cj = json.loads((cp / ".change.json").read_text())
    del cj["created"]
    (cp / ".change.json").write_text(json.dumps(cj))
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "missing 'created'" in err


# spec: spectl requirement=validate-changes scenario=fix-missing-created-date
def test_validate_fix_missing_created(spec_root):
    cp = make_change(spec_root, "bad-change", id="tmp01")
    cj = json.loads((cp / ".change.json").read_text())
    del cj["created"]
    (cp / ".change.json").write_text(json.dumps(cj))
    rc, out, err = run_spexl("validate", "--fix", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "set created" in out

    cj = json.loads((cp / ".change.json").read_text())
    assert "created" in cj


# spec: spectl requirement=validate-changes scenario=archived-merged-change-with-open-tasks
def test_validate_archived_merged_with_open_tasks(spec_root):
    make_archived_change(
        spec_root, "2026-03-14-bad-merge",
        id="mrg01", archived={"reason": "merged"},
        tasks="# Tasks\n- [x] done\n- [ ] oops\n",
    )
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "archived as merged but has 1 open tasks" in err


def test_validate_archived_rejected_with_open_tasks_ok(spec_root):
    """Rejected changes can have open tasks -- that's expected."""
    make_archived_change(
        spec_root, "2026-03-14-rejected",
        id="rej01", archived={"reason": "rejected"},
        tasks="# Tasks\n- [ ] never did this\n",
    )
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "All changes valid" in out


# spec: spectl requirement=validate-changes scenario=all-valid
def test_validate_all_valid(spec_root):
    make_change(spec_root, "good-change", id="gd001")
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "All changes valid" in out
