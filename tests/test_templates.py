# [AI]
# Context: rewrite-as-spexl (task 6.1)
# Intent: tests for template resolution module

import pytest

from spexl.templates import read_template, list_templates, _list_categories


def test_list_categories():
    cats = _list_categories()
    assert "partials" in cats
    assert "actions" in cats
    assert "artifacts" in cats
    assert "agents" in cats
    assert "concepts" in cats


def test_list_partials():
    partials = list_templates("partials")
    assert "rules.md" in partials
    assert "structure.md" in partials
    assert "cross-phase.md" in partials
    assert "file-ownership.md" in partials
    assert "interactive-vs-autonomous.md" in partials
    assert "critique.md" in partials
    # Decomposed; should not exist
    assert "skill-core.md" not in partials


def test_list_actions():
    actions = list_templates("actions")
    assert "propose.md" in actions
    assert "apply.md" in actions
    assert "explore.md" in actions
    assert "archive.md" in actions
    assert "refine.md" in actions


def test_list_artifacts():
    artifacts = list_templates("artifacts")
    assert "proposal.md" in artifacts
    assert "spec-delta.md" in artifacts
    assert "design.md" in artifacts
    assert "tasks.md" in artifacts


def test_read_template_returns_content():
    content = read_template("partials", "rules.md")
    assert "Specs are the source of truth" in content


def test_read_template_missing_raises():
    with pytest.raises(FileNotFoundError, match="not found"):
        read_template("partials", "nonexistent.md")


def test_read_template_missing_category_raises():
    with pytest.raises(FileNotFoundError, match="not found"):
        read_template("nonexistent", "rules.md")


def test_list_templates_missing_category_raises():
    with pytest.raises(FileNotFoundError, match="not found"):
        list_templates("nonexistent")
