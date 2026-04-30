## Why

spexl bundles skills, agents, and methodology content inside the Python package (`src/spexl/content/`) and relies on a custom `install` command to copy them to agent-specific directories. This conflates two concerns: the CLI (plumbing for spec management) and the content (skills, rules, subagent definitions). Separating them lets each coding agent's native plugin system handle content distribution, eliminating the install command and its per-target rendering machinery.

## What Changes

- **BREAKING**: `spexl install` command removed. Content is distributed via native plugins, not the CLI.
- **BREAKING**: `spexl onboard` command removed. Methodology primer delivered via `AGENTS.md` and `CLAUDE.md` at the plugin root.
- Skills and agent definitions promoted from `src/spexl/content/` to the repo root (`skills/`, `agents/`). Empty `commands/` and `hooks/` directories added following superpowers convention.
- `src/spexl/content/` removed entirely. The CLI no longer bundles or manages content.
- Per-agent plugin manifests added at the repo root: `.claude-plugin/`, `.opencode/`, `.pi/`.
- `cli/install.py` reduced to `init` only (project scaffolding). Install-related code removed.
- `cli/steering.py` removed (onboard command).
- `.spexl.toml` no longer records `[agents]` sections.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `skill-generation`: Replaced by plugin distribution. Content moves to repo root; `install` command and content bundling removed.
- `cli`: `install` reduced to `init`-only; `onboard` removed; package structure updated.
- `onboarding`: Removed. Content migrates to `AGENTS.md` (opencode, pi) and `CLAUDE.md` (Claude Code) at the plugin root.

## Impact

- `src/spexl/content/` -- deleted (skills, agents, onboard.md, rules)
- `src/spexl/cli/install.py` -- gutted: init logic stays, all install/refresh/remove logic deleted
- `src/spexl/cli/steering.py` -- deleted
- `src/spexl/__init__.py` -- steering registration removed
- `pyproject.toml` -- remove `importlib.resources` package-data for `spexl.content`; no new dependencies
- `config.py` -- `[agents]` section handling removed from config read/write
- Tests -- install/onboard tests rewritten or removed; init tests unchanged
- Repo root gains `skills/`, `agents/`, `commands/`, `hooks/`, `AGENTS.md`, `CLAUDE.md`, `.claude-plugin/`, `.opencode/`, `.pi/`
