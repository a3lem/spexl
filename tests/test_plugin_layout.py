# [AI]
# Context: spex-9c9a (shablon migration); claude-only plugin distribution.
# Intent: assert the rendered Claude Code plugin layout at the repo root, and that
#         no python-package content/ directory remains.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent

METHODOLOGY_SKILL = "spexl-foundations"
ACTION_SKILLS = ("spexl-explore", "spexl-propose", "spexl-refine", "spexl-apply", "spexl-archive")


# -- repo-root content layout --


def test_skills_at_repo_root() -> None:
    skills_dir = REPO_ROOT / "skills"
    assert skills_dir.is_dir()

    foundations = skills_dir / METHODOLOGY_SKILL
    assert foundations.is_dir()
    assert (foundations / "SKILL.md").is_file()
    assert (foundations / "references").is_dir()

    for action in ACTION_SKILLS:
        assert (skills_dir / action / "SKILL.md").is_file(), f"missing {action}/SKILL.md"


def test_agents_at_repo_root() -> None:
    agents_dir = REPO_ROOT / "agents"
    assert agents_dir.is_dir()
    assert (agents_dir / "spexl-spec-critic.md").is_file()
    assert (agents_dir / "spexl-spec-sync.md").is_file()


def test_content_not_in_python_package() -> None:
    assert not (REPO_ROOT / "src" / "spexl" / "content").exists()


# -- claude plugin manifest + session-start hook --


def test_claude_plugin_manifest() -> None:
    manifest_path = REPO_ROOT / ".claude-plugin" / "plugin.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text())
    assert manifest["name"] == "spexl"
    assert "description" in manifest
    assert "version" in manifest
    assert manifest["skills"] == "./skills/"
    assert manifest["agents"] == "./agents/"
    assert manifest["hooks"] == "./plugins/claude/hooks/hooks.json"


def test_session_start_hook_present() -> None:
    hooks_path = REPO_ROOT / "plugins" / "claude" / "hooks" / "hooks.json"
    assert hooks_path.is_file()
    hooks = json.loads(hooks_path.read_text())
    session_hooks = hooks["hooks"]["SessionStart"]
    assert session_hooks, "SessionStart hook list is empty"
    cmd = session_hooks[0]["hooks"][0]["command"]
    assert "prime.md" in cmd
    assert "${CLAUDE_PLUGIN_ROOT}" in cmd


def test_prime_md_wraps_in_system_reminder() -> None:
    prime_path = REPO_ROOT / "plugins" / "claude" / "hooks" / "prime.md"
    assert prime_path.is_file()
    content = prime_path.read_text()
    assert content.lstrip().startswith("<system-reminder>")
    assert "</system-reminder>" in content
    assert "spec-driven development" in content.lower()
    assert "spexl-foundations" in content


# -- shablon source of truth --


def test_shablon_templates_present() -> None:
    templates = REPO_ROOT / ".shablon" / "templates"
    assert templates.is_dir()
    assert (templates / "_includes" / "prime.md").is_file()
    assert (templates / "skills" / METHODOLOGY_SKILL / "SKILL.md").is_file()
    assert (templates / "agents" / "spexl-spec-critic.md").is_file()
    assert (templates / "plugins" / "claude" / "hooks" / "hooks.json").is_file()


# -- skill content integrity --


def test_action_skills_defer_to_methodology_skill() -> None:
    for action in ACTION_SKILLS:
        skill_path = REPO_ROOT / "skills" / action / "SKILL.md"
        body = skill_path.read_text()
        assert METHODOLOGY_SKILL in body, (
            f"{action} does not reference {METHODOLOGY_SKILL}"
        )


def test_agents_declare_methodology_skill() -> None:
    for agent in ("spexl-spec-critic.md", "spexl-spec-sync.md"):
        body = (REPO_ROOT / "agents" / agent).read_text()
        assert f"skills: {METHODOLOGY_SKILL}" in body, (
            f"{agent} does not declare skills: {METHODOLOGY_SKILL}"
        )
