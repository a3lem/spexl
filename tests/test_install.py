# [AI]
# Context: spex-9c9a (shablon migration) -- spexl install removed; only init remains.
# Intent: verify `spexl init` scaffolds .spexl.toml + specs/{changes,reference}/.

from __future__ import annotations

import tomllib
from pathlib import Path

from conftest import run_spexl


# spec: cli requirement=init-scaffolds-project scenario=init-in-empty-directory
def test_init_scaffolds_empty_directory(tmp_path: Path) -> None:
    rc, out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / ".spexl.toml").is_file()
    assert (tmp_path / "specs" / "changes").is_dir()
    assert (tmp_path / "specs" / "reference").is_dir()
    assert "initialized" in out.lower()


# spec: cli requirement=init-scaffolds-project scenario=init-in-already-initialized-directory
def test_init_in_already_initialized_directory(tmp_path: Path) -> None:
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
def test_init_backfills_missing_specs_directories(tmp_path: Path) -> None:
    (tmp_path / ".spexl.toml").write_text("")
    original_config = (tmp_path / ".spexl.toml").read_text()

    rc, _out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / "specs" / "changes").is_dir()
    assert (tmp_path / "specs" / "reference").is_dir()
    assert (tmp_path / ".spexl.toml").read_text() == original_config


# spec: cli requirement=init-scaffolds-project scenario=init-does-not-overwrite-specs
def test_init_does_not_overwrite_existing_specs(tmp_path: Path) -> None:
    user_spec = tmp_path / "specs" / "reference" / "thing" / "spec.md"
    user_spec.parent.mkdir(parents=True)
    user_spec.write_text("# user content\n")

    rc, _out, _err = run_spexl("init", cwd=tmp_path)
    assert rc == 0
    assert (tmp_path / ".spexl.toml").is_file()
    assert user_spec.read_text() == "# user content\n"


# spec: cli requirement=init-scaffolds-project scenario=init-rejects-target-argument
def test_init_rejects_target_argument(tmp_path: Path) -> None:
    rc, _out, err = run_spexl("init", "claude", cwd=tmp_path)
    assert rc == 1
    assert "no arguments" in err.lower()


# spec: cli requirement=init-scaffolds-project scenario=init-does-not-install-agents
def test_init_does_not_install_agent_files(tmp_path: Path) -> None:
    run_spexl("init", cwd=tmp_path)
    assert not (tmp_path / ".claude").exists()

    config = tomllib.loads((tmp_path / ".spexl.toml").read_text())
    assert "install_targets" not in config


# spec: cli requirement=init-scaffolds-project scenario=init-in-subdir-with-parent-project
def test_init_in_subdir_prints_parent_note(tmp_path: Path) -> None:
    (tmp_path / ".spexl.toml").write_text("")
    subdir = tmp_path / "packages" / "web"
    subdir.mkdir(parents=True)

    rc, out, _err = run_spexl("init", cwd=subdir)
    assert rc == 0
    assert (subdir / ".spexl.toml").is_file()
    assert "parent project found" in out
