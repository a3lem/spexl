# [AI]
# Context: skip-design-and-tasks-in-change-status
# Intent: tests for computed status including skip functionality

from conftest import run_spexl, make_change


DELTA = {"auth": "# auth\n## ADDED Requirements\n### Requirement: foo\n"}


# spec: cli requirement=computed-status scenario=all-artifacts-present-no-tasks-started
def test_status_ready(spec_root):
    make_change(
        spec_root, "all-open", id="rdy01",
        proposal=True, design=True,
        tasks="# Tasks\n- [ ] task 1\n- [ ] task 2\n",
        deltas=DELTA,
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "ready" in out


# spec: cli requirement=computed-status scenario=all-artifacts-present-some-tasks-done
def test_status_in_progress(spec_root):
    make_change(
        spec_root, "mixed", id="prg01",
        proposal=True, design=True,
        tasks="# Tasks\n- [x] done\n- [ ] todo\n",
        deltas=DELTA,
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "in progress" in out


# spec: cli requirement=computed-status scenario=all-artifacts-present-all-tasks-done
def test_status_complete(spec_root):
    make_change(
        spec_root, "all-done", id="cmp01",
        proposal=True, design=True,
        tasks="# Tasks\n- [x] done 1\n- [x] done 2\n",
        deltas=DELTA,
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "complete" in out


# spec: cli requirement=computed-status scenario=missing-artifact-without-skip
def test_status_drafting(spec_root):
    make_change(spec_root, "incomplete", id="inc01")
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "drafting" in out


def test_status_drafting_missing_design(spec_root):
    make_change(
        spec_root, "no-design", id="nod01",
        proposal=True,
        tasks="# Tasks\n- [ ] todo\n",
        deltas=DELTA,
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "drafting" in out


# spec: cli requirement=computed-status scenario=missing-artifact-with-skip
def test_status_skip_design(spec_root):
    make_change(
        spec_root, "skip-design", id="skd01",
        proposal=True,
        tasks="# Tasks\n- [ ] task 1\n",
        deltas=DELTA,
        skip=["design"],
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "ready" in out


# spec: cli requirement=computed-status scenario=skip-design-and-tasks
def test_status_skip_design_and_tasks(spec_root):
    make_change(
        spec_root, "skip-both", id="skb01",
        proposal=True,
        deltas=DELTA,
        skip=["design", "tasks"],
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "complete" in out


def test_status_skip_tasks_with_tasks_file_present(spec_root):
    """When tasks is skipped but tasks.md exists anyway, evaluate the checklist."""
    make_change(
        spec_root, "skip-tasks-but-has-file", id="stf01",
        proposal=True, design=True,
        tasks="# Tasks\n- [ ] not done\n",
        deltas=DELTA,
        skip=["tasks"],
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    # tasks.md exists so it gets evaluated despite skip
    assert "ready" in out


def test_status_backward_transition(spec_root):
    cp = make_change(
        spec_root, "was-complete", id="bck01",
        proposal=True, design=True,
        tasks="# Tasks\n- [x] done 1\n- [x] done 2\n",
        deltas=DELTA,
    )
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "complete" in out

    (cp / "tasks.md").write_text("# Tasks\n- [x] done 1\n- [x] done 2\n- [ ] new task\n")
    rc, out, err = run_spexl("changes", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert "in progress" in out


# spec: cli requirement=new-command-skip-flag scenario=new-with-skip
def test_new_with_skip(spec_root):
    rc, out, err = run_spexl(
        "new", "test-skip", "--skip", "design", "--skip", "tasks",
        "--cwd", str(spec_root.parent), cwd=spec_root.parent,
    )
    assert rc == 0
    import json
    cj = json.loads((spec_root / "changes" / "test-skip" / ".change.json").read_text())
    assert cj["skip"] == ["design", "tasks"]


# spec: cli requirement=new-command-skip-flag scenario=new-without-skip
def test_new_without_skip(spec_root):
    rc, out, err = run_spexl(
        "new", "test-no-skip",
        "--cwd", str(spec_root.parent), cwd=spec_root.parent,
    )
    assert rc == 0
    import json
    cj = json.loads((spec_root / "changes" / "test-no-skip" / ".change.json").read_text())
    assert "skip" not in cj


def test_new_with_invalid_skip(spec_root):
    rc, out, err = run_spexl(
        "new", "test-bad-skip", "--skip", "proposal",
        "--cwd", str(spec_root.parent), cwd=spec_root.parent,
    )
    assert rc == 1
    assert "Invalid --skip" in err


# spec: cli requirement=validate-skip-values scenario=invalid-skip-value
def test_validate_invalid_skip(spec_root):
    make_change(spec_root, "bad-skip", id="bsk01")
    import json
    cj_path = spec_root / "changes" / "bad-skip" / ".change.json"
    cj = json.loads(cj_path.read_text())
    cj["skip"] = ["proposal"]
    cj_path.write_text(json.dumps(cj, indent=2) + "\n")

    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 1
    assert "invalid skip" in err


# spec: cli requirement=validate-skip-values scenario=valid-skip-value
def test_validate_valid_skip(spec_root):
    make_change(spec_root, "good-skip", id="gsk01", skip=["design"])
    rc, out, err = run_spexl("validate", "--cwd", str(spec_root.parent), cwd=spec_root.parent)
    assert rc == 0
