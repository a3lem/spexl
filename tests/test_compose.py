# [AI]
# Context: rewrite-as-spexl (task 6.1)
# Intent: tests for skill composition engine

from spexl.generate.compose import compose_skill, SKILL_MANIFESTS


def test_compose_propose_has_frontmatter():
    content = compose_skill("propose")
    assert "---" in content
    assert "name: spexl-propose" in content
    assert "description:" in content


def test_compose_propose_has_rules():
    content = compose_skill("propose")
    assert "Specs are the source of truth" in content


def test_compose_propose_has_action():
    content = compose_skill("propose")
    assert "Propose Phase Reference" in content


def test_compose_propose_has_steering():
    content = compose_skill("propose")
    assert "spexl context propose" in content
    assert "spexl template" in content
    assert "spexl new" in content


def test_compose_propose_has_section_markers():
    content = compose_skill("propose")
    assert "<!-- spexl:rules -->" in content
    assert "<!-- spexl:action -->" in content
    assert "<!-- spexl:steering -->" in content


def test_compose_apply_has_interactive_vs_autonomous():
    content = compose_skill("apply")
    assert "Interactive vs Autonomous" in content


def test_compose_explore_is_lean():
    content = compose_skill("explore")
    # Explore only includes rules, not structure/file-ownership
    assert "Directory Structure" not in content
    assert "File Ownership" not in content


def test_compose_all_actions():
    for action_name in SKILL_MANIFESTS:
        content = compose_skill(action_name)
        assert f"name: spexl-{action_name}" in content
        assert "generated_by: spexl" in content
        assert "generated_on:" in content


def test_compose_has_version():
    content = compose_skill("propose")
    assert "generated_by: spexl 0.1.0" in content
