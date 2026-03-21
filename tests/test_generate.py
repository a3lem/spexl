# [AI]
# Context: idempotent-init change
# Intent: tests for idempotent init, config-driven refresh, --remove, subdirectory walk-up

import tomllib

from conftest import run_spexl


# spec: project-config requirement=config-file scenario=config-created-on-init
def test_init_creates_config(tmp_path):
    rc, out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 0
    config_path = tmp_path / ".spexl.toml"
    assert config_path.is_file()
    with open(config_path, "rb") as f:
        config = tomllib.load(f)
    assert config["agents"]["claude"]["install_path"] == ".claude/"


# spec: skill-generation requirement=init-target scenario=init-claude-fresh
def test_init_fresh_creates_all_files(tmp_path):
    rc, out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 0
    assert "created" in out

    # Skills
    for action in ("explore", "propose", "refine", "apply", "archive"):
        skill_file = tmp_path / ".claude" / "skills" / f"spexl-{action}" / "SKILL.md"
        assert skill_file.is_file(), f"Missing skill: {skill_file}"

    # Agents
    assert (tmp_path / ".claude" / "agents" / "spec-critic.md").is_file()
    assert (tmp_path / ".claude" / "agents" / "spec-sync.md").is_file()

    # Rules file
    rules_file = tmp_path / ".claude" / "rules" / "spexl.md"
    assert rules_file.is_file()
    assert "spexl" in rules_file.read_text().lower()

    # Config
    assert (tmp_path / ".spexl.toml").is_file()


# spec: skill-generation requirement=init-target scenario=init-fresh-no-specs
def test_init_does_not_create_specs_dir(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    assert not (tmp_path / "specs").exists()


# spec: skill-generation requirement=init-target scenario=init-claude-already-installed
def test_init_idempotent_no_changes(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    rc, out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 0
    assert "0 files changed" in out
    assert "unchanged" in out


# spec: skill-generation requirement=init-target scenario=init-claude-already-installed
def test_init_idempotent_detects_changes(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    # Corrupt one file
    skill_file = tmp_path / ".claude" / "skills" / "spexl-propose" / "SKILL.md"
    skill_file.write_text("corrupted content")
    rc, out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 0
    assert "1 files changed" in out


# spec: skill-generation requirement=init-target scenario=init-no-target-argument
def test_init_no_target_refreshes_from_config(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    # Corrupt one file
    rules_file = tmp_path / ".claude" / "rules" / "spexl.md"
    rules_file.write_text("corrupted")
    rc, out, err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert "1 files changed" in out


# spec: cli requirement=init-scaffolds-project scenario=init-in-empty-directory
def test_init_no_target_no_config_scaffolds(tmp_path):
    rc, out, err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / ".spexl.toml").is_file()
    assert (tmp_path / "specs" / "changes").is_dir()
    assert (tmp_path / "specs" / "reference").is_dir()
    assert "initialized" in out.lower()


# spec: skill-generation requirement=init-target scenario=init-unsupported-target
def test_init_unknown_target(tmp_path):
    rc, out, err = run_spexl("init", "cursor", cwd=tmp_path)
    assert rc == 1
    assert "Unknown target" in err


# spec: skill-generation requirement=init-target scenario=init-remove
def test_init_remove(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    assert (tmp_path / ".claude" / "skills").is_dir()
    assert (tmp_path / ".spexl.toml").is_file()

    rc, out, err = run_spexl("init", "--remove", cwd=tmp_path)
    assert rc == 0
    assert "removed" in out

    # Managed files gone
    assert not (tmp_path / ".claude" / "skills" / "spexl-propose" / "SKILL.md").exists()
    assert not (tmp_path / ".claude" / "agents" / "spec-critic.md").exists()
    assert not (tmp_path / ".claude" / "rules" / "spexl.md").exists()
    assert not (tmp_path / ".spexl.toml").exists()


# spec: skill-generation requirement=init-target scenario=init-remove-no-config
def test_init_remove_no_config(tmp_path):
    rc, out, err = run_spexl("init", "--remove", cwd=tmp_path)
    assert rc == 0
    assert "Nothing to remove" in out


# spec: project-config requirement=config-discovery scenario=init-from-subdirectory
def test_init_subdirectory_walks_up(tmp_path):
    # Install at project root
    run_spexl("init", "claude", cwd=tmp_path)
    # Corrupt a file
    rules_file = tmp_path / ".claude" / "rules" / "spexl.md"
    rules_file.write_text("old content")

    # Run init from a subdirectory
    subdir = tmp_path / "packages" / "web"
    subdir.mkdir(parents=True)
    rc, out, err = run_spexl("init", "claude", cwd=subdir)
    assert rc == 0
    # Should have refreshed the parent installation
    assert "changed" in out
    # File should be restored
    assert rules_file.read_text() != "old content"


# spec: skill-generation requirement=skill-composition scenario=generated-propose-skill
def test_generated_skills_reference_spexl_commands(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    propose_skill = (tmp_path / ".claude" / "skills" / "spexl-propose" / "SKILL.md").read_text()
    assert "spexl explain" in propose_skill or "spexl context" in propose_skill
    assert "spexl template" in propose_skill
    assert "spexl new" in propose_skill


# spec: skill-generation requirement=init-target scenario=init-remove (prune check)
def test_init_remove_prunes_empty_dirs(tmp_path):
    run_spexl("init", "claude", cwd=tmp_path)
    # Add a user file alongside managed files
    user_file = tmp_path / ".claude" / "settings.json"
    user_file.write_text("{}")

    run_spexl("init", "--remove", cwd=tmp_path)
    # .claude/ should still exist (has user file)
    assert (tmp_path / ".claude").is_dir()
    assert user_file.is_file()
    # But spexl subdirs should be gone
    assert not (tmp_path / ".claude" / "skills").exists()
    assert not (tmp_path / ".claude" / "agents").exists()
    assert not (tmp_path / ".claude" / "rules").exists()
