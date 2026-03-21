"""Tests for `spexl new`.
# spec: cli requirement=create-change
"""

import json
from conftest import run_spexl, make_change


# spec: cli requirement=create-change scenario=basic-creation
def test_basic_creation(spec_root):
    rc, out, err = run_spexl("new", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "Created" in out
    assert "(id:" in out

    change_path = spec_root / "changes" / "add-oauth"
    assert change_path.is_dir()
    assert (change_path / "deltas").is_dir()

    cj = json.loads((change_path / ".change.json").read_text())
    assert "id" in cj
    assert len(cj["id"]) == 5
    assert cj["id"].isalnum()
    assert "created" in cj
    assert "status" not in cj  # status is computed, not stored


# spec: cli requirement=create-change scenario=slug-collision
def test_slug_collision(spec_root):
    make_change(spec_root, "add-oauth")
    rc, out, err = run_spexl("new", "add-oauth", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "already exists" in err


# spec: cli requirement=package-structure scenario=explicit-project-directory
def test_custom_project_directory(tmp_path):
    project = tmp_path / "other-project"
    project.mkdir()
    (project / ".spexl.toml").write_text("")
    specs = project / "specs"
    specs.mkdir()
    (specs / "changes").mkdir()
    rc, out, err = run_spexl("new", "add-oauth", "--cwd", str(project), cwd=tmp_path)
    assert rc == 0
    assert (specs / "changes" / "add-oauth" / ".change.json").is_file()
