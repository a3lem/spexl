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

### Package layout: src/spexl/ with submodules

The CLI entry point lives in `__init__.py:main()`. Subcommands are grouped by concern:

- `cli/plumbing.py` – existing spectl commands (new, changes, validate, archive, info, refs, link, unlink)
- `cli/generate.py` – init, update
- `cli/steering.py` – context, template

The `generate/` subpackage handles skill composition (reading partials, assembling SKILL.md files). `templates.py` provides `importlib.resources`-based access to the `templates/` directory.

**Alternatives considered:**
- Single file (current approach): doesn't scale with the new commands and makes testing harder.
- Click/Typer CLI framework: adds a dependency for marginal ergonomic gain. argparse is sufficient and already used.

### Templates as package data

The `src/spexl/templates/` directory ships inside the installed package. Accessed via `importlib.resources` so paths resolve correctly regardless of install location.

**Alternatives considered:**
- Templates as string literals in Python: loses the ability to edit/inspect them as standalone files.
- Separate data package: unnecessary complexity for a single directory tree.

### Composition model: concatenation with section markers

Skill generation concatenates partials in a defined order, wrapped in section markers (HTML comments). This keeps the output readable and debuggable while being dead simple.

```markdown
<!-- spexl:frontmatter -->
---
name: spexl-propose
description: ...
---

<!-- spexl:rules -->
[content from partials/rules extracted from skill-core.md]

<!-- spexl:structure -->
[content from partials/structure extracted from skill-core.md]

<!-- spexl:action -->
[content from actions/propose.md]

<!-- spexl:steering -->
For runtime context: `spexl context propose`
For artifact templates: `spexl template <type>`
```

No Jinja or templating engine. Plain string concatenation.

**Alternatives considered:**
- Jinja2 templates: powerful but adds a dependency and makes templates harder to read as standalone markdown.
- Programmatic assembly with AST: over-engineered for markdown concatenation.

### Decomposing skill-core.md into focused partials

The current SKILL.md (skill-core.md) contains rules, structure, file ownership, commands, critique workflow, and directory layout in one file. For composition, it needs splitting into focused partials that can be included selectively:

- `partials/rules.md` – the 5 core rules + don'ts
- `partials/structure.md` – directory layout and conventions
- `partials/file-ownership.md` – who owns what, when to warn
- `partials/cross-phase.md` – implications of changes across phases
- `partials/critique.md` – already exists, critique checklists
- `partials/interactive-vs-autonomous.md` – mode differences

This replaces the current monolithic `skill-core.md`.

### Generated skill naming

Skills are named `spexl-<action>` (e.g., `spexl-propose`, `spexl-apply`). This scopes them to spexl and avoids collisions with other plugins. The directory name matches: `.claude/skills/spexl-propose/SKILL.md`.

## Risks / Trade-offs / Limitations

- **Token budget per skill**: Each generated skill will be ~2-3k words. If shared partials grow, skills grow too. Monitor and trim.
- **Update drift**: If users edit generated skills, `spexl update` may overwrite changes. The `# spexl:keep` marker mitigates this but adds complexity. Start simple – overwrite everything on update, add keep-markers later if needed.
- **Two sources of truth during migration**: The old plugin and spexl will coexist temporarily. The old plugin continues to work; spexl is the forward path.

## Open Questions

- Should `spexl context` compose multiple topics in one call (e.g., `spexl context rules structure`)? Defer until we see usage patterns.
- Should `spexl init claude` also generate hooks (e.g., a SessionStart hook that runs `spexl validate`)? Defer to a follow-up change.
