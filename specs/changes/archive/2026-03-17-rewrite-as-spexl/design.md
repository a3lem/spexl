## Context

Currently `spectl` is a single 861-line Python script invoked by a Claude Code skill. The skill (SKILL.md) carries all methodology knowledge but fails to load when users invoke commands from other projects. The rewrite splits concerns: spexl is a proper Python package that owns both the plumbing and the knowledge, while generated skills are thin orchestration layers that call back into spexl.

## Goals / Non-Goals

**Goals:**
- Installable as a standalone tool via `uv tool install spexl`
- Generate self-contained Claude Code skills that actually load correctly
- Serve methodology knowledge on demand via `context` and `template` commands
- Preserve all existing plumbing behavior

**Non-Goals:**
- Supporting non-Claude agents in this iteration (architecture allows it, implementation deferred)
- GUI or TUI interface
- Spec diffing or merge conflict resolution
- Plugin marketplace distribution (replaced by direct install)

## Decisions

### Package layout: src/spexl/ with per-domain CLI modules

The CLI entry point lives in `__init__.py:main()`. Each CLI module owns a specific domain and registers its own subcommands:

```
src/spexl/
├── __init__.py              # main(), top-level argparse, routes to modules
├── errors.py                # SpexlError
├── cli/
│   ├── changes.py           # new, changes, archived, info, archive
│   ├── links.py             # link, unlink
│   ├── validate.py          # validate (+ --fix)
│   ├── refs.py              # refs
│   ├── generate.py          # init, update
│   └── steering.py          # context, template
├── generate/
│   └── compose.py           # Skill composition logic
├── specroot.py              # resolve_spec_root, find_spec_roots, resolve_change
├── templates.py             # importlib.resources access to templates/
└── templates/               # Package data
```

Each `cli/*.py` module exposes a `register(subparsers)` function. `__init__.py:main()` calls each one.

Shared helpers that multiple CLI modules need (spec root discovery, change resolution, .change.json I/O) live in `specroot.py` – not in any single CLI module.

**Alternatives considered:**
- Single `plumbing.py` catch-all: same problem as `utils.py` – the name says nothing about what's inside. Splitting by domain makes each module's responsibility obvious from the filename.
- Single file (current approach): doesn't scale with the new commands and makes testing harder.
- Click/Typer CLI framework: adds a dependency for marginal ergonomic gain. argparse is sufficient and already used.

### Porting spectl.py into domain modules

The existing `spectl.py` has a clean structure: `build_parser()` → `cmd_*` functions → utility functions. The port splits it by domain:

1. `cli/changes.py` gets `cmd_new`, `cmd_changes`, `cmd_archived`, `cmd_info`, `cmd_archive` and their `register(subparsers)`.
2. `cli/links.py` gets `cmd_link`, `cmd_unlink`. These don't use spec root discovery – they take explicit paths.
3. `cli/validate.py` gets `cmd_validate` (+ `--fix`).
4. `cli/refs.py` gets `cmd_refs`.
5. `errors.py` gets `SpexlError` (renamed from `SpectlError`).
6. `specroot.py` gets the shared helpers: `resolve_spec_root`, `find_spec_roots`, `resolve_change`, `read_change_json`, `write_change_json`, `generate_id`, `computed_status`. These are used by multiple CLI modules (changes, validate, refs all need spec root discovery).

The key constraint: no behavioral changes. Existing tests must pass with just import path changes.

### Templates as package data

The `src/spexl/templates/` directory ships inside the installed package. Accessed via `importlib.resources` so paths resolve correctly regardless of install location.

`templates.py` exposes two functions:

```python
def read_template(category: str, name: str) -> str:
    """Read a template file. e.g. read_template("artifacts", "proposal.md")"""

def list_templates(category: str) -> list[str]:
    """List available templates in a category. e.g. list_templates("partials")"""
```

Both use `importlib.resources.files("spexl.templates")` internally.

**Alternatives considered:**
- Templates as string literals in Python: loses the ability to edit/inspect them as standalone files.
- Separate data package: unnecessary complexity for a single directory tree.

### Decomposing skill-core.md into focused partials

The current SKILL.md (164 lines) contains everything in one file. For composition, it needs splitting into focused partials that can be included selectively per generated skill:

| Partial | Source lines | Content |
|---------|-------------|---------|
| `rules.md` | Lines 46-57 | 5 core rules + don'ts |
| `structure.md` | Lines 93-119 | Directory layout, delta targeting, monorepo |
| `file-ownership.md` | Lines 33-43 | Ownership table + "changing spec invalidates design" warning |
| `cross-phase.md` | Lines 132-139 | Iteration, apply snags → design flaws, scope changes |
| `interactive-vs-autonomous.md` | Lines 121-131 | Mode differences, when to pause |
| `critique.md` | Lines 141-156 | Already exists separately; critique modes, verdicts, escalation |

The existing `partials/spec.md`, `partials/design.md`, `partials/tasks.md`, `partials/verification.md` stay as-is – these are artifact-writing guidance, not shared skill rules.

### Composition model: concatenation with section markers

Skill generation concatenates partials in a defined order, wrapped in section markers (HTML comments). Dead simple, no templating engine.

```markdown
<!-- Generated by spexl 0.1.0 on 2026-03-17. Do not edit unless you know what you're doing. -->
---
name: spexl-propose
description: This skill should be used when the user asks to "propose a change", "create a spec", "start a new feature", or wants to define requirements for a new capability.
---

# Propose

<!-- spexl:rules -->
[partials/rules.md content]

<!-- spexl:structure -->
[partials/structure.md content]

<!-- spexl:file-ownership -->
[partials/file-ownership.md content]

<!-- spexl:cross-phase -->
[partials/cross-phase.md content]

<!-- spexl:action -->
[actions/propose.md content, adapted for standalone use]

<!-- spexl:steering -->
## Runtime Context

For additional context during execution:
- `spexl context propose` – full phase-specific guidance
- `spexl template <type>` – artifact templates (proposal, spec-delta, design, tasks)
- `spexl new change <slug>` – scaffold the change directory
- `spexl validate --change <slug>` – check structural integrity
```

Each action gets a different subset of partials and different action content. The compose function takes a manifest per action:

```python
SKILL_MANIFESTS = {
    "propose": {
        "description": 'This skill should be used when the user asks to "propose a change"...',
        "partials": ["rules", "structure", "file-ownership", "cross-phase"],
        "action": "propose",
    },
    "apply": {
        "description": 'This skill should be used when the user asks to "implement"...',
        "partials": ["rules", "structure", "file-ownership", "cross-phase", "interactive-vs-autonomous"],
        "action": "apply",
    },
    # ...
}
```

### Generated skill naming and location

Skills are named `spexl-<action>` (e.g., `spexl-propose`, `spexl-apply`). Directories: `.claude/skills/spexl-propose/SKILL.md`. This scopes them to spexl and avoids collisions with other plugins.

### Action template adaptation

The current `templates/actions/*.md` files reference things like "read [references/spec.md](references/spec.md)" and "use `templates/proposal.md`" – paths relative to a SKILL.md that won't exist in the generated context. These references need rewriting to use `spexl` CLI commands:

- "Read [references/spec.md](references/spec.md)" → "Run `spexl context spec-notation` for notation guidance"
- "Use `templates/proposal.md`" → "Run `spexl template proposal` to get the template"
- "Run `python3 scripts/spectl.py new <slug>`" → "Run `spexl new <slug>`"

This adaptation happens once as a manual edit to the action templates, not at generation time.

### Update detection

`spexl update` detects whether regeneration is needed by comparing the `<!-- Generated by spexl X.Y.Z ... -->` comment in each existing skill against the current spexl version. If versions differ, regenerate. If same version, skip (print "Already up to date").

No content hashing for now – version comparison is sufficient and simple.

### Init output structure

`spexl init claude` generates:

```
.claude/
├── skills/
│   ├── spexl-propose/SKILL.md
│   ├── spexl-apply/SKILL.md
│   ├── spexl-explore/SKILL.md
│   ├── spexl-refine/SKILL.md
│   └── spexl-archive/SKILL.md
└── agents/
    ├── spec-critic.md
    └── spec-sync.md
specs/
├── reference/
└── changes/
```

Agents are copied verbatim from `templates/agents/`. Skills are composed. `specs/` dirs are created only if missing.

## Risks / Trade-offs / Limitations

- **Token budget per skill**: Each generated skill will be ~2-3k words from partials alone. If shared partials grow, skills grow too. Monitor and trim. The `context` command is the pressure valve – move verbose content out of partials and into context-only topics.
- **Update drift**: If users edit generated skills, `spexl update` overwrites them. Start with full overwrite; add `<!-- spexl:keep -->` markers later if users actually need customization.
- **Two sources of truth during migration**: The old plugin and spexl coexist temporarily. The old plugin continues to work; spexl is the forward path.
- **Action template adaptation is manual**: The action templates need one-time editing to replace relative paths with `spexl` CLI calls. This is a one-time cost but must be done carefully.

## Open Questions

- Should `spexl context` compose multiple topics in one call (e.g., `spexl context rules structure`)? Defer until we see usage patterns.
- Should `spexl init claude` also generate hooks (e.g., a SessionStart hook that runs `spexl validate`)? Defer to a follow-up change.
- Should the refine skill include routing logic inline, or should it call `spexl context refine-routing` at runtime? Leaning toward inline since the routing table is small (~10 lines).
