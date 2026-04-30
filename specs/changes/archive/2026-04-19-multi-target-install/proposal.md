## Why

spexl currently installs agent integration files for Claude Code only, copying bundled content verbatim. To support multiple coding agents (Claude Code, opencode, pi) -- and handle per-agent content differences like tool-specific instructions and hook mechanisms -- the install command needs per-target rendering and per-target file routing.

## What Changes

- **BREAKING**: `spexl install <target>` becomes `spexl install --target <target>` (or `-t`). The `--target` flag is mandatory for first install; omit it to refresh all configured targets.
- Install renders Jinja2 templates with per-target context instead of copying files verbatim. Templates live in `src/spexl/content/templates/`.
- Supported targets expand from `claude` to `claude`, `opencode`, `pi`.
- Each target has a destination mapping (where skills, rules, hooks, and prompts go).
- Claude Code hooks are installed by merging definitions into `.claude/settings.json`. opencode and pi hooks are installed by dropping files.
- Installed files include a managed-file marker (comment identifying them as spexl-managed).
- The `onboard` command is removed. Its content becomes a rules file installed by `install`.
- `--remove` gains target awareness: it reads `.spexl.toml` to know which targets were installed and what to clean up.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `skill-generation`: Multi-target support, template rendering, hook installation, managed-file markers, rules file generation (absorbs onboard content)
- `cli`: Install command surface changes (`--target`/`-t` flag, `onboard` removal)
- `onboarding`: Removed entirely; content moves into skill-generation as a rendered rules file

## Impact

- `cli/install.py`: Major rewrite. Template rendering replaces `_walk_resource`/`_managed_files` verbatim copy. Per-target adapter logic for destination paths and hook installation.
- `cli/steering.py`: Removed (onboard command).
- `__init__.py`: Remove steering module registration, update install registration.
- `content/`: Restructured. Current `skills/`, `agents/` replaced by `templates/` containing Jinja2 templates. Template context varies by target.
- `pyproject.toml`: Add `jinja2` dependency.
- `.spexl.toml`: `[agents.<target>]` sections unchanged in structure, but the CLI reads `install_path` differently per target (some targets split across two directories).
- Tests: install tests rewritten for template rendering and multi-target scenarios.

## Alternatives Considered

- **Native plugins per platform**: Lower maintenance (no install logic), but fragmented UX (different install incantation per agent), version drift between CLI and plugin artifacts, and no coverage for agents without plugin systems. See `docs/why-install-instead-of-plugins.md`.
- **Build-time rendering + static variants**: Keeps Jinja out of the runtime package but ships all target variants in every install. Simpler CLI, fatter package. Viable but less flexible if per-target differences grow.
