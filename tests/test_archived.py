"""Tests for `spexl changes --archived`.
# spec: cli requirement=changes-archived-filter
"""

from conftest import run_spexl, make_archived_change


# spec: cli requirement=changes-archived-filter scenario=archived-flag
def test_list_archived(spec_root):
    make_archived_change(
        spec_root, "2026-03-14-add-oauth",
        id="x7k2m", archived={"reason": "merged"},
    )
    make_archived_change(
        spec_root, "2026-03-10-old-feature",
        id="r3t8w", archived={"reason": "rejected"},
    )
    rc, out, err = run_spexl("changes", "--archived", cwd=spec_root.parent)
    assert rc == 0
    assert "x7k2m" in out
    assert "merged" in out
    assert "r3t8w" in out
    assert "rejected" in out


# spec: cli requirement=changes-archived-filter scenario=default-shows-active-only
def test_no_archived(spec_root):
    rc, out, err = run_spexl("changes", "--archived", cwd=spec_root.parent)
    assert rc == 0
    assert "No changes" in out
