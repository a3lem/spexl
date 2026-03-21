"""Tests for spec directory discovery.
# spec: cli requirement=recursive-discovery-by-default
# spec: cli requirement=package-structure
"""

from conftest import run_spexl


# spec: cli requirement=recursive-discovery-by-default scenario=single-project
def test_default_discovery(spec_root):
    rc, out, err = run_spexl("changes", cwd=spec_root.parent)
    assert rc == 0
    assert "No changes" in out


# spec: cli requirement=recursive-discovery-by-default scenario=no-marker-file
def test_no_spexl_toml(tmp_path):
    """No .spexl.toml anywhere -- walk-down finds nothing, prints 'No changes'."""
    rc, out, err = run_spexl("changes", cwd=tmp_path)
    assert rc == 0
    assert "No changes" in out


# spec: cli requirement=recursive-discovery-by-default scenario=no-recurse-flag
def test_no_spexl_toml_no_recurse(tmp_path):
    """With --no-recurse and no .spexl.toml, walk-up errors."""
    rc, out, err = run_spexl("changes", "--no-recurse", cwd=tmp_path)
    assert rc == 1
    assert "spexl init" in err


# spec: cli requirement=package-structure scenario=explicit-project-directory
def test_explicit_directory(tmp_path):
    project = tmp_path / "other-project"
    project.mkdir()
    (project / ".spexl.toml").write_text("")
    specs = project / "specs"
    specs.mkdir()
    (specs / "changes").mkdir()
    rc, out, err = run_spexl("changes", "--cwd", str(project), "--no-recurse", cwd=tmp_path)
    assert rc == 0
    assert "No changes" in out


# spec: cli requirement=recursive-discovery-by-default scenario=subdir-does-not-walk-up
def test_subdir_does_not_show_parent_specs(spec_root):
    """Running from a subdirectory does NOT walk up – only looks down."""
    from conftest import make_change
    make_change(spec_root, "parent-change", id="par01")
    subdir = spec_root.parent / "src" / "deep"
    subdir.mkdir(parents=True)
    rc, out, err = run_spexl("changes", cwd=subdir)
    assert rc == 0
    assert "No changes" in out  # parent's change is NOT shown


# spec: cli requirement=recursive-discovery-by-default scenario=false-positive-prevention
def test_false_positive_dirs_ignored(spec_root):
    """Dirs named 'changes' without .spexl.toml are not treated as spec roots."""
    fake = spec_root.parent / "docs" / "changes" / "some-subdir"
    fake.mkdir(parents=True)
    rc, out, err = run_spexl("changes", cwd=spec_root.parent)
    assert rc == 0
    # Should only show spec_root's (empty) changes, not docs/changes
    assert "docs" not in out
