"""Tests for change identifier resolution.
# spec: spectl requirement=change-identifier-resolution
"""

from conftest import run_spexl, make_change


# spec: spectl requirement=change-identifier-resolution scenario=resolve-by-slug
def test_resolve_by_slug(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("info", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth" in out


# spec: spectl requirement=change-identifier-resolution scenario=resolve-by-id
def test_resolve_by_id(spec_root):
    make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("info", "x7k2m", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth" in out


# spec: spectl requirement=change-identifier-resolution scenario=resolve-by-path
def test_resolve_by_path(spec_root):
    cp = make_change(spec_root, "add-oauth", id="x7k2m")
    rc, out, err = run_spexl("info", str(cp), "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "add-oauth" in out


# spec: spectl requirement=change-identifier-resolution scenario=no-match
def test_resolve_no_match(spec_root):
    rc, out, err = run_spexl("info", "nonexistent", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "No change found" in err
