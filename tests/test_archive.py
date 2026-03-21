"""Tests for `spectl archive`.
# spec: spectl requirement=archive-change
"""

import json
from conftest import run_spexl, make_change


# spec: spectl requirement=archive-change scenario=move-to-archive
def test_archive_moves_to_dated_directory(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("archive", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "Archived to" in out

    # Original is gone
    assert not (spec_root / "changes" / "add-oauth").exists()

    # Archived dir exists with date prefix
    archive_dir = spec_root / "changes" / "archive"
    archived = list(archive_dir.iterdir())
    assert len(archived) == 1
    assert archived[0].name.endswith("-add-oauth")

    # .change.json has archived field
    cj = json.loads((archived[0] / ".change.json").read_text())
    assert cj["archived"] == {"reason": "merged"}


# spec: spectl requirement=archive-change scenario=sync-summary
def test_archive_sync_summary(spec_root):
    delta_content = (
        "# user-auth\n"
        "## ADDED Requirements\n"
        "### Requirement: Login\n"
        "## MODIFIED Requirements\n"
        "### Requirement: Password reset\n"
        "### Requirement: Session timeout\n"
    )
    make_change(spec_root, "add-oauth", id="x7k2m", deltas={"user-auth": delta_content})
    rc, out, err = run_spexl("archive", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "Sync summary:" in out
    assert "user-auth:" in out
    assert "1 added" in out
    assert "2 modified" in out


# spec: spectl requirement=archive-change scenario=sync-summary
def test_archive_sync_summary_new_capability(spec_root):
    delta_content = (
        "# oauth\n"
        "## ADDED Requirements\n"
        "### Requirement: OAuth flow\n"
        "### Requirement: Token refresh\n"
        "### Requirement: Provider config\n"
    )
    make_change(spec_root, "add-oauth", id="x7k2m", deltas={"oauth-provider": delta_content})
    # No reference/oauth-provider/ exists → NEW capability
    rc, out, err = run_spexl("archive", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "NEW capability" in out
    assert "3 added" in out


# spec: spectl requirement=archive-change scenario=incomplete-tasks-guard
def test_archive_incomplete_tasks_guard(spec_root):
    make_change(
        spec_root, "add-oauth", id="x7k2m",
        tasks="# Tasks\n- [x] done\n- [ ] not done\n",
    )
    rc, out, err = run_spexl("archive", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "1 incomplete tasks remain" in err
    # Change should still exist
    assert (spec_root / "changes" / "add-oauth").is_dir()


# spec: spectl requirement=archive-change scenario=force-archive-with-incomplete-tasks
def test_archive_force_with_incomplete_tasks(spec_root):
    make_change(
        spec_root, "add-oauth", id="x7k2m",
        tasks="# Tasks\n- [ ] not done\n",
    )
    rc, out, err = run_spexl(
        "archive", "add-oauth", "--force", "--cwd", str(spec_root.parent),
        cwd=spec_root.parent,
    )
    assert rc == 0
    assert "Archived to" in out


# spec: spectl requirement=archive-change scenario=reject-a-change
def test_archive_rejected(spec_root):
    make_change(spec_root, "bad-idea", id="bad01")
    rc, out, err = run_spexl(
        "archive", "bad-idea", "--rejected", "--cwd", str(spec_root.parent),
        cwd=spec_root.parent,
    )
    assert rc == 0
    assert "Sync summary" not in out

    archive_dir = spec_root / "changes" / "archive"
    archived = list(archive_dir.iterdir())
    cj = json.loads((archived[0] / ".change.json").read_text())
    assert cj["archived"] == {"reason": "rejected"}


# spec: spectl requirement=archive-change scenario=dry-run
def test_archive_dry_run(spec_root):
    delta_content = (
        "# auth\n"
        "## ADDED Requirements\n"
        "### Requirement: Login\n"
    )
    make_change(spec_root, "add-oauth", id="x7k2m", deltas={"auth": delta_content})
    rc, out, err = run_spexl(
        "archive", "add-oauth", "--dry-run", "--cwd", str(spec_root.parent),
        cwd=spec_root.parent,
    )
    assert rc == 0
    assert "Sync summary:" in out
    # Change should still exist
    assert (spec_root / "changes" / "add-oauth").is_dir()
    # Archive should not exist
    assert not (spec_root / "changes" / "archive").exists()


def test_archive_resolve_by_id(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("archive", "x7k2m", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert not (spec_root / "changes" / "add-oauth").exists()
