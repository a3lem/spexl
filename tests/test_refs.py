"""Tests for `spectl refs`.
# spec: spectl requirement=list-reference-specs
"""

from conftest import run_spexl


# spec: spectl requirement=list-reference-specs scenario=list-references
def test_list_refs(spec_root):
    for name in ("billing", "user-auth"):
        cap_dir = spec_root / "reference" / name
        cap_dir.mkdir(parents=True)
        (cap_dir / "spec.md").write_text(f"# {name}\n## Overview\nHandles {name} logic.\n")

    rc, out, err = run_spexl("refs", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "user-auth" in out
    assert "billing" in out
    assert "Handles user-auth logic" in out


# spec: spectl requirement=list-reference-specs scenario=no-references
def test_no_refs(spec_root):
    rc, out, err = run_spexl("refs", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
    assert "No reference specs" in out


# spec: cli requirement=recursive-discovery-by-default scenario=recursive-refs
def test_recursive_refs(tmp_path):
    """refs discovers reference dirs across multiple spec roots."""
    (tmp_path / ".spexl.toml").write_text("")  # root marker
    for project in ("proj-a", "proj-b"):
        proj_dir = tmp_path / project
        proj_dir.mkdir()
        (proj_dir / ".spexl.toml").write_text("")
        ref_dir = proj_dir / "specs" / "reference" / f"{project}-cap"
        ref_dir.mkdir(parents=True)
        (ref_dir / "spec.md").write_text(f"# {project}-cap\n## Overview\n{project} capability.\n")

    rc, out, err = run_spexl("refs", cwd=tmp_path)
    assert rc == 0
    assert "proj-a-cap" in out
    assert "proj-b-cap" in out
