# [AI]
# Context: replace-context-with-prime-and-explain
# Intent: tests for prime, explain, and template steering commands

from conftest import run_spexl


# spec: knowledge-priming requirement=prime-command scenario=prime-output
def test_prime_output():
    rc, out, err = run_spexl("prime")
    assert rc == 0
    # Foundational methodology content
    assert "source of truth" in out.lower()
    assert "reference spec" in out.lower() or "Reference spec" in out
    assert "spec delta" in out.lower() or "Spec Delta" in out or "ADDED" in out
    # Directory structure
    assert "specs/" in out
    assert "reference/" in out
    assert "changes/" in out
    # Key terms
    assert "Capability" in out
    assert "Requirement" in out
    assert "Scenario" in out


# spec: knowledge-priming requirement=prime-command scenario=prime-output
def test_prime_excludes_phase_instructions():
    rc, out, err = run_spexl("prime")
    assert rc == 0
    # Should NOT include phase-specific procedural instructions
    assert "Propose Phase Reference" not in out
    assert "Apply Phase Reference" not in out
    # Should NOT include full critique checklists (but may reference modes briefly)
    assert "Checklist" not in out


# spec: runtime-steering requirement=explain-command scenario=explain-a-topic
def test_explain_spec_notation():
    rc, out, err = run_spexl("explain", "spec-notation")
    assert rc == 0
    assert "SHALL" in out
    assert len(out) > 100


# spec: runtime-steering requirement=explain-command scenario=explain-spexl-methodology
def test_explain_spexl():
    rc, out, err = run_spexl("explain", "spexl")
    assert rc == 0
    assert "The Big Idea" in out or "source of truth" in out.lower()
    assert len(out) > 500


# spec: runtime-steering requirement=explain-command scenario=explain-unknown-topic
def test_explain_unknown_topic():
    rc, out, err = run_spexl("explain", "nonexistent")
    assert rc == 1
    assert "unknown topic" in err


def test_explain_no_topic():
    rc, out, err = run_spexl("explain")
    assert rc == 1
    assert "topic required" in err


# spec: runtime-steering requirement=explain-command scenario=list-explain-topics
def test_explain_list():
    rc, out, err = run_spexl("explain", "--list")
    assert rc == 0
    assert "spec-notation" in out
    assert "verification" in out
    assert "critique" in out
    assert "spexl" in out
    assert "design" in out
    assert "tasks" in out


# spec: runtime-steering requirement=template-command scenario=list-available-templates
def test_template_list():
    rc, out, err = run_spexl("template", "--list")
    assert rc == 0
    assert "proposal" in out
    assert "spec-delta" in out
    assert "design" in out
    assert "tasks" in out


# spec: runtime-steering requirement=template-command scenario=print-proposal-template
def test_template_proposal():
    rc, out, err = run_spexl("template", "proposal")
    assert rc == 0
    assert "## Why" in out


# spec: runtime-steering requirement=template-command scenario=print-spec-delta-template
def test_template_spec_delta():
    rc, out, err = run_spexl("template", "spec-delta")
    assert rc == 0
    assert "ADDED" in out


# spec: runtime-steering requirement=template-command scenario=print-design-template
def test_template_design():
    rc, out, err = run_spexl("template", "design")
    assert rc == 0
    assert "Context" in out or "Goals" in out


# spec: runtime-steering requirement=template-command scenario=print-tasks-template
def test_template_tasks():
    rc, out, err = run_spexl("template", "tasks")
    assert rc == 0
    assert "- [ ]" in out or "Tasks" in out


# spec: runtime-steering requirement=template-command scenario=print-reference-spec-template
def test_template_reference_spec():
    rc, out, err = run_spexl("template", "reference-spec")
    assert rc == 0
    assert "Overview" in out or "Requirements" in out


# spec: runtime-steering requirement=template-command scenario=unknown-artifact-type
def test_template_unknown_type():
    rc, out, err = run_spexl("template", "nonexistent")
    assert rc == 1
    assert "unknown artifact type" in err


def test_template_no_type():
    rc, out, err = run_spexl("template")
    assert rc == 1
    assert "artifact type required" in err
