# [AI]
# Context: drop-composition change -- prime/explain/template collapsed into a single onboard command
# Intent: verify onboard prints the primer to stdout and the paste instruction to stderr

from conftest import run_spexl


# spec: onboarding requirement=onboard-command scenario=default-output
def test_onboard_prints_primer_to_stdout():
    rc, out, err = run_spexl("onboard")
    assert rc == 0
    # Core content the agent needs to see after paste
    assert "spec-driven development" in out.lower()
    assert "specs are the source of truth" in out.lower()
    # Skill routing
    assert "spexl-propose" in out
    assert "spexl-apply" in out
    # Rules
    assert "Rules" in out
    # Methodology skill pointer
    assert "spexl-foundations" in out


# spec: onboarding requirement=onboard-command scenario=piped-to-agents-md
def test_onboard_instruction_goes_to_stderr():
    rc, out, err = run_spexl("onboard")
    assert rc == 0
    # The "Add this to..." header is guidance, not content to paste; stderr keeps pipes clean
    assert "AGENTS.md" in err
    assert "CLAUDE.md" in err
    assert "AGENTS.md" not in out
    assert "CLAUDE.md" not in out
