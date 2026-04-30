## Context

spexl bundles skills, agents, and methodology content inside the Python package at `src/spexl/content/`. The `install` command copies these to agent-specific directories. This change separates the CLI (plumbing) from the content (skills, rules, agents) and distributes content via native plugin mechanisms for Claude Code, opencode, and pi.

The rejected `multi-target-install` change (archived 2026-04-19) explored an install-command approach with Jinja2 templates. Key learning: templates are unnecessary if skills are written at the intent level and per-agent tool mappings live in agent-specific rules. See `docs/why-install-instead-of-plugins.md`.

The repo layout follows the pattern established by [superpowers](https://github.com/obra/superpowers): all shared content at the repo root, thin per-agent plugin manifests pointing at it.

## Goals / Non-Goals

**Goals:**
- Promote skills, agents, and rules to the repo root
- Create plugin manifests for claude, opencode, and pi
- Remove `install`, `onboard`, and content bundling from the CLI
- Simplify `config.py` by removing `[agents]` handling

**Non-Goals:**
- Skill rewriting to agent-agnostic phrasing (separate future change)
- Supporting agents beyond claude, opencode, pi
- Templating or build steps (not needed currently)
- Hook installation (out of scope for spexl, relevant for epimem/tiquette)

## Decisions

### Repo layout

Modeled after superpowers. All shared content lives at the repo root. Per-agent plugin directories are thin -- just manifests and agent-specific overrides.

```
spexl/
├── skills/                            # Shared skills
│   ├── spexl-foundations/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── rules.md
│   │       ├── concepts.md
│   │       ├── spec-notation.md
│   │       ├── structure.md
│   │       ├── verification.md
│   │       ├── critique.md
│   │       ├── design-guidance.md
│   │       ├── tasks-guidance.md
│   │       ├── modes.md
│   │       └���─ templates/
│   ├── spexl-explore/SKILL.md
│   ├── spexl-propose/SKILL.md
│   ├── spexl-refine/SKILL.md
│   ├── spexl-apply/SKILL.md
│   └── spexl-archive/SKILL.md
├── agents/                            # Shared agent definitions
│   ├── spexl-spec-critic.md
│   └── spexl-spec-sync.md
├── commands/                          # Shared commands (empty for now)
├── hooks/                             # Hook definitions, per-agent variants inside
│   └── hooks.json                     # Claude Code hooks (empty for now)
├── AGENTS.md                          # Methodology primer (replaces onboard.md)
├── CLAUDE.md                          # Claude-specific rules/tool mappings
├── .claude-plugin/                    # Claude Code plugin manifest
│   └── plugin.json
├── .opencode/                         # opencode plugin
│   └── INSTALL.md
├── .pi/                               # pi plugin
│   └── INSTALL.md
├─��� src/spexl/                         # CLI (plumbing only)
│   ├── __init__.py
│   ├���─ errors.py
│   ├── specroot.py
│   ├── config.py
│   └── cli/
│       ���── changes.py
��       ├── links.py
│       ├── validate.py
│       ├── refs.py
│       └── install.py                 # init only
├── specs/
├── tests/
├── pyproject.toml
└── .spexl.toml
```

Key differences from the current layout:
- `src/spexl/content/` is gone. All content lives at the repo root.
- `AGENTS.md` at plugin root replaces `rules/sdd-with-spexl.md` and the old `onboard` command. Agents that support AGENTS.md (pi, opencode) load it automatically. Claude Code loads `CLAUDE.md`.
- `hooks/` at the root follows superpowers' convention. Per-agent hook variants live inside (e.g., `hooks.json` for Claude, `hooks-cursor.json` for Cursor in superpowers). Empty for spexl currently.
- `commands/` at the root for saved prompts. Empty for spexl currently but present for convention.

### Plugin manifests

Following superpowers exactly:

**Claude Code** (`.claude-plugin/plugin.json`):

```json
{
  "name": "spexl",
  "description": "Spec-driven development: propose, explore, refine, apply, archive",
  "version": "0.1.0",
  "author": {
    "name": "Adriaan",
    "email": "a3lem@pm.me"
  },
  "homepage": "https://github.com/a3lem/spexl",
  "repository": "https://github.com/a3lem/spexl",
  "license": "MIT",
  "keywords": ["specs", "sdd", "spec-driven-development"]
}
```

Claude Code auto-discovers `skills/`, `agents/`, `commands/`, and `hooks/` relative to the plugin root. No explicit paths needed (superpowers' Claude plugin.json also omits them -- Claude Code infers them by convention).

`CLAUDE.md` at the plugin root is loaded as plugin-provided context. This is where Claude-specific tool-mapping rules live ("when skills reference AskUserQuestion, use it" -- though since skills currently use Claude-specific names, the mapping is identity for Claude).

**Cursor** (`.cursor-plugin/plugin.json`, if added later):

Would follow superpowers' Cursor manifest pattern with explicit paths:

```json
{
  "skills": "./skills/",
  "agents": "./agents/",
  "commands": "./commands/",
  "hooks": "./hooks/hooks-cursor.json"
}
```

Not created in this change -- only claude, opencode, and pi are targets.

**opencode** (`.opencode/`):

opencode plugins are referenced by git URL in the project's `opencode.json`:

```json
{"plugin": ["spexl@git+https://github.com/a3lem/spexl.git"]}
```

opencode auto-discovers skills and rules from the repo root. `AGENTS.md` is loaded as context. An `INSTALL.md` in `.opencode/` documents the installation step.

**pi** (`.pi/`):

pi reads skills from the plugin root's `skills/` directory and loads `AGENTS.md` as context. An `INSTALL.md` in `.pi/` documents the installation step.

[CLARIFICATION NEEDED] The exact pi plugin manifest format needs verification. The `.pi/` directory may need a `package.json` or similar manifest.

### AGENTS.md and CLAUDE.md as rules

Instead of a `rules/` directory, follow superpowers' convention:

- **`AGENTS.md`** at plugin root: methodology primer (the old `onboard.md` content). Loaded by agents that support AGENTS.md (opencode, pi). Contains: five-phase workflow, core rules, directory layout, pointer to spexl-foundations skill.
- **`CLAUDE.md`** at plugin root: Claude-specific context. Contains: same methodology primer plus Claude-specific tool-mapping notes (e.g., confirming that `AskUserQuestion` references in skills should be taken literally).

Note: the plugin-level `CLAUDE.md` is distinct from the project-level `CLAUDE.md` that already exists for spexl development. The plugin system namespaces them -- the plugin's `CLAUDE.md` is loaded as plugin context, not as project context.

### Skill rewriting

Out of scope for this change. Skills are promoted as-is. Agent-specific references (e.g., `AskUserQuestion` in propose/apply, tool-name pseudo-code in critique.md) remain. Per-agent context files (CLAUDE.md, AGENTS.md) handle any necessary translation. A separate change can rewrite skills to agent-agnostic phrasing later if needed.

### Agent definitions per target

Agent definitions live at `agents/` in the repo root (same as superpowers' `agents/code-reviewer.md`). Exposure per target:

| Target | Agent support | Delivery |
|--------|--------------|----------|
| claude | Full (model, tools, skills frontmatter) | Auto-discovered from `agents/` |
| opencode | Partial (subset of frontmatter fields) | [CLARIFICATION NEEDED] May need investigation |
| pi | None | Not exposed (pi ignores `agents/`) |

Agent definitions use Claude-format frontmatter. If opencode can't consume them, that's acceptable -- opencode gets skills and rules but not subagents, same as pi.

### config.py surgery

Remove:
- `ProjectConfig.agents` field and its parsing in `from_toml()`
- `ProjectConfig.has_install_path` property
- `find_project_root()` (only used to locate install path)
- `write_config()` `agents` parameter and all agents-related output logic
- `update_config()` function entirely (only used by install)

Keep:
- `ProjectConfig` with `toml_path` and `specs_location`
- `find_nearest_config()`, `discover_all_configs()`, `discover_single_config()`
- `write_config()` simplified to specs_location only
- `read_config()` unchanged

`write_config()` signature simplifies from:

```python
def write_config(path, agents=None, specs_location=None)
```

to:

```python
def write_config(path, specs_location=None)
```

### install.py surgery

Remove:
- `SUPPORTED_TARGETS`, `_managed_files()`, `_walk_resource()`, `_do_install()`, `_do_refresh()`, `_do_remove()`, `_strip_agents()`, `_prune_empty_dirs()`, `_default_install_path()`
- `cmd_install()` function
- The `install` subparser registration

Keep:
- `cmd_init()` and its subparser registration
- `_scaffold_project()`, `_ensure_specs_dirs()`, `_find_existing_config()`, `_find_parent_config()`

Add:
- Friendly error stubs in `__init__.py` for `install` and `onboard` subcommands that print migration guidance and exit 1.

### Migration order

To avoid breaking the test suite mid-change:

1. **Create repo-root content.** Copy (not move) `src/spexl/content/skills/` → `skills/`, `content/agents/` → `agents/`. Create `AGENTS.md` from `content/onboard.md`. Create plugin-level `CLAUDE.md`. Create empty `commands/` and `hooks/` dirs.
2. **Create plugin manifests.** Add `.claude-plugin/plugin.json`, `.opencode/INSTALL.md`, `.pi/INSTALL.md`.
3. **Strip CLI.** Remove install logic from `install.py`. Delete `steering.py`. Remove content bundling from pyproject.toml. Simplify `config.py`. Add friendly error stubs.
4. **Delete old content.** Remove `src/spexl/content/` entirely.
5. **Update tests.** Delete install/onboard tests. Add tests for friendly error stubs. Verify init still works.
6. **Update docs.** Project-level CLAUDE.md structure section, CHANGELOG.

Steps 1-2 are additive (nothing breaks). Step 3-4 are the breaking change. Step 5-6 are cleanup.

### pyproject.toml changes

Remove the `spexl.content` package from `[tool.setuptools.packages.find]` or equivalent. No new dependencies are added. The package becomes pure CLI.

If `importlib.resources` references exist in the package config for `content/`, remove them. The `content/` subpackage and its `__init__.py` are deleted.

## Risks / Trade-offs / Limitations

**[Agent-specific references in skills]** → Skills are promoted as-is with references like `AskUserQuestion`. Plugin-level CLAUDE.md and AGENTS.md provide per-agent context. A future change can rewrite skills to agent-agnostic phrasing if the rules approach proves insufficient.

**[opencode agent format uncertainty]** → The opencode agent frontmatter subset isn't fully documented. May need investigation during implementation. Worst case: opencode gets no subagent support initially, same as pi.

**[Two-step install for users]** → Users need `uv tool install spexl` (CLI) AND the plugin install for their agent. These are independent -- CLI for plumbing, plugin for methodology. Neither depends on the other for basic functionality.

**[Plugin-level vs project-level CLAUDE.md]** → The plugin's CLAUDE.md is distinct from the project's CLAUDE.md. Claude Code namespaces them correctly via the plugin system. But if someone clones the spexl repo to develop on it, both exist -- the plugin-level one is for plugin consumers, the project-level one is for spexl developers.

## Open Questions

- What does pi's plugin manifest look like? Does pi auto-discover from a plugin root, or does it need explicit configuration?
- Which opencode agent frontmatter fields are supported? This determines whether `agents/` files work as-is for opencode.
- Should `commands/` and `hooks/` be created empty, or omitted until they have content? Superpowers has content in both; creating empty dirs signals intent but adds clutter.
