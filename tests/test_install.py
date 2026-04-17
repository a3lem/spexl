# [AI]
# Context: split-init-install -- `init` scaffolds the project, `install` manages agent assets
# Intent: verify the two commands don't overlap: init never touches agent files,
#         install never creates specs/, and remove leaves .spexl.toml in place

from __future__ import annotations

import importlib.resources
import tomllib
from collections.abc import Iterator
from importlib.resources.abc import Traversable
from pathlib import Path

from conftest import run_spexl

METHODOLOGY_SKILL = "spexl-foundations"
ACTION_SKILLS = ("explore", "propose", "refine", "apply", "archive")


def _walk(resource: Traversable, prefix: Path) -> Iterator[tuple[Path, Traversable]]:
    for child in resource.iterdir():
        if child.name.startswith("__") or child.name.startswith("."):
            continue
        dest = prefix / child.name
        if child.is_dir():
            yield from _walk(child, dest)
        else:
            yield dest, child


def _expected_tree(install_root: Path) -> dict[Path, str]:
    """Return {absolute_dest_path: expected_content} for every file install should place."""
    content = importlib.resources.files("spexl.content")
    tree: dict[Path, str] = {}
    for dest, resource in _walk(content.joinpath("skills"), install_root / "skills"):
        tree[dest] = resource.read_text(encoding="utf-8")
    for dest, resource in _walk(content.joinpath("agents"), install_root / "agents"):
        tree[dest] = resource.read_text(encoding="utf-8")
    return tree


# -- init: project scaffold --


# spec: cli requirement=init-scaffolds-project scenario=init-in-empty-directory
def test_init_scaffolds_empty_directory(tmp_path):
    rc, out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / ".spexl.toml").is_file()
    assert (tmp_path / "specs" / "changes").is_dir()
    assert (tmp_path / "specs" / "reference").is_dir()
    assert "initialized" in out.lower()


# spec: cli requirement=init-scaffolds-project scenario=init-in-already-initialized-directory
def test_init_in_already_initialized_directory(tmp_path):
    run_spexl("init", cwd=tmp_path)
    original_config = (tmp_path / ".spexl.toml").read_text()
    sentinel = tmp_path / "specs" / "changes" / "user-file.md"
    sentinel.write_text("user content")

    rc, out, err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert "spexl already initialized in this directory" in err
    assert out == ""
    assert (tmp_path / ".spexl.toml").read_text() == original_config
    assert sentinel.read_text() == "user content"


# spec: cli requirement=init-scaffolds-project scenario=init-backfills-missing-specs-directories
def test_init_backfills_missing_specs_directories(tmp_path):
    (tmp_path / ".spexl.toml").write_text("")
    original_config = (tmp_path / ".spexl.toml").read_text()

    rc, _out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / "specs" / "changes").is_dir()
    assert (tmp_path / "specs" / "reference").is_dir()
    assert (tmp_path / ".spexl.toml").read_text() == original_config


# spec: cli requirement=init-scaffolds-project scenario=init-does-not-overwrite-specs
def test_init_does_not_overwrite_existing_specs(tmp_path):
    user_spec = tmp_path / "specs" / "reference" / "thing" / "spec.md"
    user_spec.parent.mkdir(parents=True)
    user_spec.write_text("# user content\n")

    rc, _out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / ".spexl.toml").is_file()
    assert user_spec.read_text() == "# user content\n"


# spec: cli requirement=init-scaffolds-project scenario=init-rejects-target-argument
def test_init_rejects_target_argument(tmp_path):
    rc, _out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 1
    assert "spexl install claude" in err


# spec: cli requirement=init-scaffolds-project scenario=init-does-not-install-agents
def test_init_does_not_install_agent_files(tmp_path):
    run_spexl("init", cwd=tmp_path)
    assert not (tmp_path / ".claude").exists()

    config = tomllib.loads((tmp_path / ".spexl.toml").read_text())
    assert "agents" not in config


# spec: cli requirement=init-scaffolds-project scenario=init-in-subdir-with-parent-project
def test_init_in_subdir_prints_parent_note(tmp_path):
    (tmp_path / ".spexl.toml").write_text("")
    subdir = tmp_path / "packages" / "web"
    subdir.mkdir(parents=True)

    rc, out, _err = run_spexl("init", cwd=subdir)
    assert rc == 0
    assert (subdir / ".spexl.toml").is_file()
    assert "parent project found" in out


# -- install: agent assets --


# spec: skill-generation requirement=install-target scenario=install-claude-fresh
def test_install_fresh_mirrors_source_tree(tmp_path):
    rc, out, _err = run_spexl("install", "claude", cwd=tmp_path)
    assert rc == 0
    assert "created" in out

    install_root = tmp_path / ".claude"
    expected = _expected_tree(install_root)

    for dest, source_content in expected.items():
        assert dest.is_file(), f"missing {dest}"
        assert dest.read_text() == source_content, f"content mismatch at {dest}"

    installed: set[Path] = set()
    for managed_dir in ("skills", "agents"):
        root = install_root / managed_dir
        if root.is_dir():
            installed |= {p for p in root.rglob("*") if p.is_file()}
    assert installed == set(expected), (
        f"installed tree differs from source. "
        f"extra: {installed - set(expected)}, missing: {set(expected) - installed}"
    )

    # onboard primer is CLI output, not a file on disk
    assert not (tmp_path / ".claude" / "rules" / "spexl.md").exists()

    # config created with the target entry
    config_path = tmp_path / ".spexl.toml"
    assert config_path.is_file()
    config = tomllib.loads(config_path.read_text())
    assert config["agents"]["claude"]["install_path"] == ".claude/"


# spec: skill-generation requirement=install-target scenario=install-claude-fresh
def test_install_does_not_create_specs_dir(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    assert not (tmp_path / "specs").exists()


# spec: skill-generation requirement=install-target scenario=install-claude-already-installed
def test_install_idempotent_no_changes(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    rc, out, _err = run_spexl("install", "claude", cwd=tmp_path)
    assert rc == 0
    assert "0 files changed" in out
    assert "unchanged" in out


# spec: skill-generation requirement=install-target scenario=install-claude-already-installed
def test_install_idempotent_detects_changes(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    skill_file = tmp_path / ".claude" / "skills" / "spexl-propose" / "SKILL.md"
    skill_file.write_text("corrupted content")
    rc, out, _err = run_spexl("install", "claude", cwd=tmp_path)
    assert rc == 0
    assert "1 files changed" in out


# spec: skill-generation requirement=install-target scenario=install-with-no-target-argument
def test_install_no_target_refreshes_from_config(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    target = tmp_path / ".claude" / "skills" / METHODOLOGY_SKILL / "SKILL.md"
    target.write_text("corrupted")
    rc, out, _err = run_spexl("install", cwd=tmp_path)
    assert rc == 0
    assert "1 files changed" in out


# spec: skill-generation requirement=install-target scenario=install-with-no-target-and-no-config
def test_install_no_target_no_config_errors(tmp_path):
    rc, _out, err = run_spexl("install", cwd=tmp_path)
    assert rc == 1
    assert "spexl init" in err
    assert "spexl install <target>" in err


# spec: skill-generation requirement=install-target scenario=install-with-no-target-and-no-agents-configured
def test_install_no_target_no_agents_errors(tmp_path):
    (tmp_path / ".spexl.toml").write_text("")
    rc, _out, err = run_spexl("install", cwd=tmp_path)
    assert rc == 1
    assert "No agents configured" in err


# spec: skill-generation requirement=install-target scenario=install-unsupported-target
def test_install_unknown_target(tmp_path):
    rc, _out, err = run_spexl("install", "cursor", cwd=tmp_path)
    assert rc == 1
    assert "Unknown target" in err


# spec: skill-generation requirement=install-target scenario=install-remove
def test_install_remove(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    assert (tmp_path / ".claude" / "skills").is_dir()
    assert (tmp_path / ".spexl.toml").is_file()

    rc, out, _err = run_spexl("install", "--remove", cwd=tmp_path)
    assert rc == 0
    assert "removed" in out

    # Managed files gone
    assert not (tmp_path / ".claude" / "skills" / "spexl-propose" / "SKILL.md").exists()
    assert not (tmp_path / ".claude" / "agents" / "spexl-spec-critic.md").exists()


# spec: skill-generation requirement=install-target scenario=install-remove
def test_install_remove_preserves_config_file(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    rc, _out, _err = run_spexl("install", "--remove", cwd=tmp_path)
    assert rc == 0

    config_path = tmp_path / ".spexl.toml"
    assert config_path.is_file()
    config = tomllib.loads(config_path.read_text())
    assert "agents" not in config


# spec: skill-generation requirement=install-target scenario=install-remove-no-config
def test_install_remove_no_config(tmp_path):
    rc, out, _err = run_spexl("install", "--remove", cwd=tmp_path)
    assert rc == 0
    assert "Nothing to remove" in out


# spec: skill-generation requirement=install-target scenario=install-remove (prune check)
def test_install_remove_prunes_empty_dirs(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    user_file = tmp_path / ".claude" / "settings.json"
    user_file.write_text("{}")

    run_spexl("install", "--remove", cwd=tmp_path)
    # .claude/ still exists (has user file)
    assert (tmp_path / ".claude").is_dir()
    assert user_file.is_file()
    # But spexl subdirs are gone
    assert not (tmp_path / ".claude" / "skills").exists()
    assert not (tmp_path / ".claude" / "agents").exists()


# spec: project-config requirement=install-path-inheritance scenario=leaf-inherits-from-root
def test_install_subdirectory_walks_up(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    target = tmp_path / ".claude" / "skills" / METHODOLOGY_SKILL / "SKILL.md"
    target.write_text("old content")

    subdir = tmp_path / "packages" / "web"
    subdir.mkdir(parents=True)
    rc, out, _err = run_spexl("install", "claude", cwd=subdir)
    assert rc == 0
    assert "changed" in out
    assert target.read_text() != "old content"


# -- methodology skill / agent frontmatter (cross-cutting, still routes through install) --


# spec: skill-generation requirement=methodology-skill scenario=methodology-skill-installed-with-references
def test_methodology_skill_references_install(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    refs_dir = tmp_path / ".claude" / "skills" / METHODOLOGY_SKILL / "references"
    for name in (
        "rules.md",
        "concepts.md",
        "spec-notation.md",
        "structure.md",
        "verification.md",
        "critique.md",
        "design-guidance.md",
        "tasks-guidance.md",
        "modes.md",
    ):
        assert (refs_dir / name).is_file(), f"missing reference file: {name}"


# spec: skill-generation requirement=methodology-skill scenario=action-skill-references-the-methodology-skill
def test_action_skills_defer_to_methodology_skill(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    for action in ACTION_SKILLS:
        skill_path = (
            tmp_path / ".claude" / "skills" / f"spexl-{action}" / "SKILL.md"
        )
        assert skill_path.is_file(), f"spexl-{action}/SKILL.md not installed"
        body = skill_path.read_text()
        assert METHODOLOGY_SKILL in body, (
            f"spexl-{action} does not reference {METHODOLOGY_SKILL}"
        )
        assert f"{METHODOLOGY_SKILL}/" not in body, (
            f"spexl-{action} references a path inside {METHODOLOGY_SKILL}/ -- "
            f"action skills should defer routing to the methodology skill"
        )
        assert "references/" not in body, (
            f"spexl-{action} names files inside references/ -- "
            f"action skills should not know the methodology skill's internal layout"
        )


# spec: skill-generation requirement=agent-generation scenario=install-spexl-spec-critic-agent-for-claude
# spec: skill-generation requirement=agent-generation scenario=install-spexl-spec-sync-agent-for-claude
def test_agents_declare_methodology_skill(tmp_path):
    run_spexl("install", "claude", cwd=tmp_path)
    for agent in ("spexl-spec-critic.md", "spexl-spec-sync.md"):
        body = (tmp_path / ".claude" / "agents" / agent).read_text()
        assert f"skills: {METHODOLOGY_SKILL}" in body, (
            f"{agent} frontmatter does not declare skills: {METHODOLOGY_SKILL}"
        )


# -- CLI surface tests --


# spec: cli requirement=install-command scenario=install-help
def test_install_help(tmp_path):
    rc, out, _err = run_spexl("install", "--help", cwd=tmp_path)
    assert rc == 0
    assert "--remove" in out
    assert "claude" in out


# spec: cli requirement=cli-entry-point scenario=invoke-init-or-install
def test_top_level_help_lists_both_commands(tmp_path):
    rc, out, _err = run_spexl("--help", cwd=tmp_path)
    assert rc == 0
    assert "init" in out
    assert "install" in out
