"""Tests for cross-project change linking.
# spec: spectl requirement=link-changes
# spec: spectl requirement=unlink-changes
# spec: spectl requirement=validate-links
"""

import json
from pathlib import Path

from conftest import run_spexl


def make_monorepo(tmp_path):
    """Create two projects with their own specs dirs and one change each."""
    proj_a = tmp_path / "services" / "api"
    proj_b = tmp_path / "libs" / "auth"

    specs_a = proj_a / "specs"
    specs_b = proj_b / "specs"

    for proj in (proj_a, proj_b):
        proj.mkdir(parents=True, exist_ok=True)
        (proj / ".spexl.toml").write_text("")
        specs = proj / "specs"
        (specs / "changes").mkdir(parents=True)
        (specs / "reference").mkdir(parents=True)

    change_a = specs_a / "changes" / "add-oauth"
    change_a.mkdir()
    (change_a / "deltas").mkdir()
    (change_a / ".change.json").write_text(json.dumps({
        "id": "abc12", "created": "2026-03-16"
    }, indent=2) + "\n")

    change_b = specs_b / "changes" / "add-token-refresh"
    change_b.mkdir()
    (change_b / "deltas").mkdir()
    (change_b / ".change.json").write_text(json.dumps({
        "id": "def34", "created": "2026-03-16"
    }, indent=2) + "\n")

    return change_a, change_b, specs_a, specs_b


# --- link-changes ---


# spec: spectl requirement=link-changes scenario=basic-link
def test_link_basic(tmp_path):
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)
    rc, out, err = run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    assert rc == 0
    assert "Linked" in out

    data_a = json.loads((change_a / ".change.json").read_text())
    data_b = json.loads((change_b / ".change.json").read_text())

    assert len(data_a["links"]) == 1
    assert data_a["links"][0]["change"] == "def34"
    assert len(data_b["links"]) == 1
    assert data_b["links"][0]["change"] == "abc12"

    # Verify specs paths are relative and resolve correctly
    resolved_b = (specs_a / data_a["links"][0]["specs"]).resolve()
    assert resolved_b == specs_b.resolve()
    resolved_a = (specs_b / data_b["links"][0]["specs"]).resolve()
    assert resolved_a == specs_a.resolve()


# spec: spectl requirement=link-changes scenario=idempotent-link
def test_link_idempotent(tmp_path):
    change_a, change_b, _, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    rc, out, err = run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    assert rc == 0

    data_a = json.loads((change_a / ".change.json").read_text())
    assert len(data_a["links"]) == 1  # not duplicated


# spec: spectl requirement=link-changes scenario=link-to-nonexistent-change
def test_link_nonexistent_path(tmp_path):
    change_a, _, _, _ = make_monorepo(tmp_path)
    rc, out, err = run_spexl("link", str(change_a), str(tmp_path / "nope"), cwd=tmp_path)
    assert rc == 1
    assert "not found" in err.lower()


# --- unlink-changes ---


# spec: spectl requirement=unlink-changes scenario=basic-unlink
def test_unlink_basic(tmp_path):
    change_a, change_b, _, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    rc, out, err = run_spexl("unlink", str(change_a), str(change_b), cwd=tmp_path)
    assert rc == 0
    assert "Unlinked" in out

    data_a = json.loads((change_a / ".change.json").read_text())
    data_b = json.loads((change_b / ".change.json").read_text())
    assert "links" not in data_a
    assert "links" not in data_b


# spec: spectl requirement=unlink-changes scenario=unlink-nonexistent-link
def test_unlink_nonexistent_link(tmp_path):
    change_a, change_b, _, _ = make_monorepo(tmp_path)
    # No link exists -- should succeed silently
    rc, out, err = run_spexl("unlink", str(change_a), str(change_b), cwd=tmp_path)
    assert rc == 0


# spec: spectl requirement=unlink-changes scenario=empty-links-array-cleanup
def test_unlink_removes_links_key(tmp_path):
    change_a, change_b, _, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    run_spexl("unlink", str(change_a), str(change_b), cwd=tmp_path)

    data_a = json.loads((change_a / ".change.json").read_text())
    assert "links" not in data_a  # key removed, not empty array


# --- validate-links ---


# spec: spectl requirement=validate-links scenario=broken-link-detected
def test_validate_broken_link_missing_specs(tmp_path):
    change_a, _, specs_a, _ = make_monorepo(tmp_path)
    # Manually add a link to a nonexistent specs dir
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": "../../nonexistent/specs", "change": "xyz99"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 1
    assert "broken link" in err


# spec: spectl requirement=validate-links scenario=broken-link-to-missing-change
def test_validate_broken_link_missing_change(tmp_path):
    change_a, _, specs_a, specs_b = make_monorepo(tmp_path)
    # Link to real specs dir but wrong change ID
    import os
    rel = os.path.relpath(specs_b, specs_a)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": rel, "change": "nonexistent"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 1
    assert "broken link" in err


# spec: spectl requirement=validate-links scenario=asymmetric-link-detected
def test_validate_asymmetric_link(tmp_path):
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)
    # Add link A -> B but not B -> A
    import os
    rel = os.path.relpath(specs_b, specs_a)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": rel, "change": "def34"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 1
    assert "asymmetric" in err


# spec: spectl requirement=validate-links scenario=fix-asymmetric-link
def test_validate_fix_asymmetric_link(tmp_path):
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)
    import os
    rel = os.path.relpath(specs_b, specs_a)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": rel, "change": "def34"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--fix", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    assert "back-link" in out

    # Verify B now links back to A
    data_b = json.loads((change_b / ".change.json").read_text())
    assert "links" in data_b
    assert any(l["change"] == "abc12" for l in data_b["links"])


# --- change-info link scenarios ---


# spec: spectl requirement=change-info scenario=info-with-resolved-links
def test_info_with_resolved_links(tmp_path):
    change_a, change_b, specs_a, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)

    rc, out, err = run_spexl("info", "add-oauth", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    assert "links:" in out
    assert "def34" in out
    assert "add-token-refresh" in out


# spec: spectl requirement=change-info scenario=info-with-broken-link
def test_info_with_broken_link(tmp_path):
    change_a, _, specs_a, _ = make_monorepo(tmp_path)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": "../../nonexistent/specs", "change": "xyz99"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("info", "add-oauth", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    assert "[broken]" in out
    assert "xyz99" in out


# spec: spectl requirement=change-info scenario=info-with-links-as-json
def test_info_with_links_json(tmp_path):
    change_a, change_b, specs_a, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)

    rc, out, err = run_spexl("info", "add-oauth", "--json", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    data = json.loads(out)
    assert "links" in data
    assert data["links"][0]["change"] == "def34"
    assert data["links"][0]["slug"] == "add-token-refresh"
    assert data["links"][0]["status"] == "drafting"


# spec: spectl requirement=change-info scenario=info-with-broken-link-as-json
def test_info_with_broken_link_json(tmp_path):
    change_a, _, specs_a, _ = make_monorepo(tmp_path)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": "../../nonexistent/specs", "change": "xyz99"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("info", "add-oauth", "--json", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    data = json.loads(out)
    assert data["links"][0]["status"] == "broken"
    assert "slug" not in data["links"][0]


# --- archive-change link scenarios ---


# spec: spectl requirement=archive-change scenario=archive-with-active-linked-changes
def test_archive_warns_active_links(tmp_path):
    change_a, change_b, specs_a, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)

    rc, out, err = run_spexl(
        "archive", "add-oauth", "--force", "--cwd", str(specs_a.parent), cwd=tmp_path
    )
    assert rc == 0
    assert "Linked changes still active:" in out
    assert "def34" in out
    assert "add-token-refresh" in out


# spec: spectl requirement=archive-change scenario=archive-with-broken-linked-change
def test_archive_warns_broken_links(tmp_path):
    change_a, _, specs_a, _ = make_monorepo(tmp_path)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": "../../nonexistent/specs", "change": "xyz99"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl(
        "archive", "add-oauth", "--force", "--cwd", str(specs_a.parent), cwd=tmp_path
    )
    assert rc == 0
    assert "[broken]" in out


# spec: spectl requirement=archive-change scenario=archive-rejected-with-active-linked-changes
def test_archive_rejected_still_warns(tmp_path):
    change_a, change_b, specs_a, _ = make_monorepo(tmp_path)
    run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)

    rc, out, err = run_spexl(
        "archive", "add-oauth", "--rejected", "--cwd", str(specs_a.parent), cwd=tmp_path
    )
    assert rc == 0
    assert "Linked changes still active:" in out


# --- validate-changes link scenarios ---


# spec: spectl requirement=validate-changes scenario=broken-link-detected
def test_validate_reports_broken_link(tmp_path):
    change_a, _, specs_a, _ = make_monorepo(tmp_path)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": "../../nonexistent/specs", "change": "xyz99"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 1
    assert "broken link" in err


# spec: spectl requirement=validate-changes scenario=asymmetric-link-detected
def test_validate_reports_asymmetric(tmp_path):
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)
    import os
    rel = os.path.relpath(specs_b, specs_a)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": rel, "change": "def34"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 1
    assert "asymmetric" in err


# spec: spectl requirement=validate-changes scenario=fix-asymmetric-link
def test_validate_fixes_asymmetric(tmp_path):
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)
    import os
    rel = os.path.relpath(specs_b, specs_a)
    data_a = json.loads((change_a / ".change.json").read_text())
    data_a["links"] = [{"specs": rel, "change": "def34"}]
    (change_a / ".change.json").write_text(json.dumps(data_a, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--fix", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    data_b = json.loads((change_b / ".change.json").read_text())
    assert any(l["change"] == "abc12" for l in data_b.get("links", []))


# --- end-to-end correctness check ---


def test_full_lifecycle(tmp_path):
    """End-to-end: link -> info -> validate -> archive -> validate again."""
    change_a, change_b, specs_a, specs_b = make_monorepo(tmp_path)

    # 1. Link the two changes
    rc, out, err = run_spexl("link", str(change_a), str(change_b), cwd=tmp_path)
    assert rc == 0
    data_a = json.loads((change_a / ".change.json").read_text())
    data_b = json.loads((change_b / ".change.json").read_text())
    assert len(data_a["links"]) == 1
    assert len(data_b["links"]) == 1

    # 2. Info shows links on both sides
    rc, out, err = run_spexl("info", "add-oauth", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    assert "def34" in out
    assert "add-token-refresh" in out

    rc, out, err = run_spexl("info", "add-token-refresh", "--cwd", str(specs_b.parent), cwd=tmp_path)
    assert rc == 0
    assert "abc12" in out
    assert "add-oauth" in out

    # 3. Validate passes (symmetric links, both exist)
    rc, out, err = run_spexl("validate", "--cwd", str(specs_a.parent), cwd=tmp_path)
    assert rc == 0
    assert "All changes valid" in out

    rc, out, err = run_spexl("validate", "--cwd", str(specs_b.parent), cwd=tmp_path)
    assert rc == 0

    # 4. Archive change A -- warns about active companion
    rc, out, err = run_spexl(
        "archive", "add-oauth", "--force", "--cwd", str(specs_a.parent), cwd=tmp_path
    )
    assert rc == 0
    assert "Linked changes still active:" in out
    assert "def34" in out

    # 5. Validate from B's side -- link to A is now broken (A was archived/moved)
    rc, out, err = run_spexl("validate", "--cwd", str(specs_b.parent), cwd=tmp_path)
    assert rc == 1
    assert "broken link" in err
