# spexl: spec-driven development

This project uses spexl for spec-driven development. Specs are the source of truth; code serves specs.

## Workflow

Five phases, each a skill that triggers on relevant user requests:

- `spexl-explore` -- investigate before committing; read code, ask questions, draw diagrams. No implementation.
- `spexl-propose` -- create a change: proposal → spec deltas → design (optional) → tasks (optional).
- `spexl-refine` -- update any existing artifact in a change.
- `spexl-apply` -- implement the change; write code and tests that satisfy every requirement and scenario.
- `spexl-archive` -- merge deltas into reference specs, move the change to `changes/archive/`.

Phases can be revisited. An apply snag may reveal a spec gap; changing a spec may invalidate the design.

For the full methodology (concepts, notation, rules, critique, verification), load the `spexl-foundations` skill.

## Rules

1. Specs are the source of truth. Code serves specs.
2. `specs/` is for specs only. No code files. `deltas/` contains only `spec.md` files.
3. Don't fabricate. Only document what was discussed or confirmed.
4. Prove your work. Never claim "done" without passing tests.
5. Mark unknowns with `[CLARIFICATION NEEDED]` and resolve them before proceeding.

## Directory Layout

```
specs/
├── reference/<capability>/spec.md    # source of truth
└── changes/
    ├── archive/<date>-<slug>/        # completed changes
    └── <slug>/                       # active change
        ├── proposal.md
        ├── deltas/<capability>/spec.md
        ├── design.md                 # optional
        ├── tasks.md                  # optional
        └── notes/                    # optional
```

## Plumbing CLI

- `spexl new <slug>` -- scaffold a new change directory
- `spexl changes` -- list active changes
- `spexl info <slug>` -- show change overview
- `spexl refs` -- list reference specs
- `spexl validate` -- check changes for structural problems
- `spexl archive <slug>` -- archive a completed change

## Notes for Claude Code

- Tool names in skill instructions (`Read`, `Edit`, `Grep`, `Glob`, `Agent`) are Claude Code tools. Use them literally.
- Subagent definitions in `agents/` (`spexl-spec-critic`, `spexl-spec-sync`) are available via the `Agent` tool.
- Skills are loaded via the `Skill` tool or by referencing them in agent `skills:` frontmatter.
