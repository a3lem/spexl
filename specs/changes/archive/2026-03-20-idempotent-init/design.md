## Context

`generate.py` currently has `cmd_init` and `cmd_update` as separate functions with version-based drift detection. The init command creates skills, agents, rules, and specs dirs. The update command compares frontmatter versions. Both are registered as separate subcommands in `__init__.py`.

This change collapses both into a single idempotent `cmd_init`, adds `.spexl.toml` for persistent config, adds `--remove`, and drops `specs/` creation.

## Goals / Non-Goals

**Goals:** Single idempotent init command, config-driven refresh, clean removal, subdirectory safety.

**Non-Goals:** Supporting multiple agent targets simultaneously (only `claude` for now, but the config format supports it). Multi-root monorepo init (walk-up finds one config, updates one install).

## Decisions

### Config file format

`.spexl.toml` at the project root. Minimal structure:

```toml
[agents.claude]
install_path = ".claude"
```

The `[agents.<target>]` table uses the target name as key. `install_path` is relative to the config file's parent directory. This supports future targets without schema changes.

Use `tomllib` (stdlib since 3.11) for reading. Use `tomli_w` for writing -- there's no stdlib TOML writer. Alternative: write TOML by hand since the format is trivially simple (two lines). Hand-writing avoids a new dependency.

**Decision: hand-write TOML.** The output is two lines. A dependency isn't justified.

### Config discovery

New function `find_config() -> tuple[Path, dict] | None` in `generate.py`. Walks from `cwd` upward checking for `.spexl.toml` at each level. Stops at filesystem root. Returns `(config_path, parsed_config)` or `None`.

### Managed file registry

Init needs to know which files it owns so it can compare, overwrite, and remove them. Rather than scanning the filesystem, build the list programmatically:

```python
def _managed_files(install_path: Path) -> dict[Path, Callable[[], str]]:
    """Map of relative file paths to content-generating functions."""
    files = {}
    for action_name in SKILL_MANIFESTS:
        p = install_path / "skills" / f"spexl-{action_name}" / "SKILL.md"
        files[p] = lambda a=action_name: compose_skill(a)
    for agent_name in ("spec-critic.md", "spec-sync.md"):
        p = install_path / "agents" / agent_name
        files[p] = lambda n=agent_name: read_template("agents", n)
    files[install_path / "rules" / "spexl.md"] = lambda: read_template("prime", "prime.md")
    return files
```

This registry drives all three operations:
- **Install**: generate content, write all files
- **Refresh**: generate content, compare to disk, overwrite if different
- **Remove**: delete each file, then prune empty parent directories

### Init flow

```
cmd_init(args):
    if args.remove:
        return _do_remove()

    config = find_config()

    if args.target:
        # Explicit target given
        if config and args.target in config[1].get("agents", {}):
            # Already installed, refresh
            _do_refresh(config, args.target)
        else:
            # Fresh install
            _do_install(args.target, config)
    else:
        # No target, need config
        if not config:
            error("No target specified and no .spexl.toml found. Supported targets: claude")
        # Refresh all configured targets
        for target in config[1]["agents"]:
            _do_refresh(config, target)
```

### Argparse changes

`init` subparser:
- `target` becomes `nargs="?"` (optional positional)
- Add `--remove` flag (`store_true`)

`update` subparser: removed entirely. Remove `generate.cmd_update` from `no_root_commands` in `__init__.py`.

### Output format

All operations print a per-file summary:

```
  unchanged  .claude/skills/spexl-propose/SKILL.md
  changed    .claude/skills/spexl-apply/SKILL.md
  changed    .claude/rules/spexl.md
  unchanged  .claude/agents/spec-critic.md

3 files changed, 5 unchanged
```

For `--remove`:
```
  removed  .claude/skills/spexl-propose/SKILL.md
  ...
  removed  .spexl.toml

8 files removed
```

### Removing empty directories

After file removal, walk the install path bottom-up and remove empty directories. Don't remove the install path itself (`.claude/`) since it may contain user files. Use `Path.iterdir()` to check emptiness before removing.

### Dropping specs/ creation

Remove the `specs/reference` and `specs/changes` mkdir block from init entirely. `spexl new` already creates `specs/changes/<slug>/` with `parents=True`, so the directory structure is created on first use.

Need to verify that `spexl new` also creates `specs/reference/` -- if not, that's fine, it'll be created on first archive.

## Risks / Trade-offs

- **Hand-written TOML** → fragile if the config format grows. Acceptable for now since it's two lines. Revisit if more fields are added.
- **Walk-up discovery** → could find a `.spexl.toml` in an unexpected parent (e.g., home directory). Mitigated by only walking to filesystem root and printing the resolved path so the user sees where it landed.
- **No locking** → concurrent `spexl init` calls could race. Acceptable for a CLI tool.
