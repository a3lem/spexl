## 1. Promote content to repo root

- [x] Copy `src/spexl/content/skills/` to `skills/` at repo root
- [x] Copy `src/spexl/content/agents/` to `agents/` at repo root
- [x] Create `AGENTS.md` from `src/spexl/content/onboard.md` (methodology primer for opencode, pi)
- [x] Create plugin-level `CLAUDE.md` (methodology primer + Claude-specific tool-mapping notes)
- [x] Create empty `commands/` directory (superpowers convention, empty for now)
- [x] Create `hooks/` directory with empty `hooks.json` (superpowers convention)
- [x] Promote skills as-is (skill rewriting is a separate future change)
- [x] Delete `src/spexl/content/` directory entirely

## 2. Create plugin manifests

- [x] Create `.claude-plugin/plugin.json` (metadata only; Claude auto-discovers skills/, agents/, commands/, hooks/)
- [x] Create `.opencode/INSTALL.md` documenting installation step
- [x] Create `.pi/INSTALL.md` documenting installation step (no agents -- pi does not support subagents)

## 3. Strip install/onboard from CLI

- [x] Remove all install/refresh/remove logic from `cli/install.py` (keep init only)
- [x] Delete `cli/steering.py` (onboard command)
- [x] Remove steering module registration from `__init__.py`
- [x] Add friendly error stubs for `spexl install` and `spexl onboard`
- [x] Remove `[agents]` handling from `config.py` (read_config, write_config, update_config)
- [x] Update pyproject.toml: remove `spexl.content` package-data, remove any content-related config

## 4. Update project files

- [x] Update CLAUDE.md project structure section
- [x] Update `.spexl.toml` (remove `[agents]` section if present)

## 5. Verification

- [x] Tests for requirement: repo-root-content-layout
- [x] Tests for requirement: per-agent-plugin-manifests
- [x] Tests for requirement: per-agent-context-via-AGENTS.md-and-CLAUDE.md
- [x] Tests for requirement: package-structure (no content in package)
- [x] Tests for requirement: subcommand-routing (init only in install module)
- [x] Tests for requirement: invoke-removed-subcommands (install, onboard friendly errors)

## Notes

- Existing install tests become obsolete and should be deleted, not adapted.
- The `config.py` changes are the most surgical part: `write_config`, `update_config`, and `_strip_agents` all reference the `[agents]` section. These functions simplify or disappear.
- Skills are promoted as-is with agent-specific references (e.g., AskUserQuestion). Per-agent context files (CLAUDE.md, AGENTS.md) handle any necessary translation. Skill rewriting to agent-agnostic phrasing is a separate future change.
- Migration order: steps 1-2 are additive (nothing breaks), steps 3-4 are breaking, step 5 is cleanup.
