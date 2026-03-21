# [AI]
# Context: rewrite-as-spexl (task 6 – gap coverage)
# Intent: tests for CLI entry point scenarios from cli/spec.md

from conftest import run_spexl


# spec: cli requirement=cli-entry-point scenario=invoke-with-no-arguments
def test_no_arguments_prints_usage_exits_0(tmp_path):
    rc, out, err = run_spexl(cwd=tmp_path)
    assert rc == 0
    assert "usage:" in out.lower() or "usage:" in err.lower()


# spec: cli requirement=cli-entry-point scenario=invoke-with-unknown-subcommand
def test_unknown_subcommand_exits_1(tmp_path):
    rc, out, err = run_spexl("nonexistent-cmd", cwd=tmp_path)
    assert rc != 0


# spec: cli requirement=version-flag scenario=print-version
def test_version_flag():
    rc, out, err = run_spexl("--version")
    assert rc == 0
    assert "spexl" in out
    assert "0.1.0" in out


# spec: cli requirement=subcommand-routing scenario=help-for-specific-subcommand
def test_subcommand_help():
    rc, out, err = run_spexl("new", "--help")
    assert rc == 0
    assert "slug" in out.lower()


# spec: cli requirement=cli-entry-point scenario=invoke-removed-subcommand
def test_archived_subcommand_removed(tmp_path):
    rc, out, err = run_spexl("archived", cwd=tmp_path)
    assert rc != 0
