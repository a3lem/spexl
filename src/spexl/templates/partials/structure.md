## Directory Structure

```
specs/
├── reference/                        # Source of truth
│   ├── authentication/
│   │   └── spec.md
│   └── billing/
│       └── spec.md
└── changes/
    ├── archive/                      # Completed changes
    │   └── 2026-03-01-initial-auth/
    └── add-oauth/                    # Active change
        ├── proposal.md               # Why (intent, scope, capabilities)
        ├── deltas/                   # What (per-capability behavioral changes)
        │   ├── session-management/
        │   │   └── spec.md
        │   └── user-auth/
        │       └── spec.md
        ├── design.md                 # How (optional)
        ├── tasks.md                  # Steps (optional)
        └── notes/                    # Learnings (optional)
```

A delta at `deltas/user-auth/spec.md` targets `reference/user-auth/spec.md`. Changes are identified by slug -- look for matching slugs in `specs/changes/*/`.

**Monorepo:** Each sub-project has its own `specs/` directory. `spexl` discovers them with `-r` (recursive). Use `--dir` to target a specific one.
