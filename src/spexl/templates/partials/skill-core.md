---
name: spec-driven-development
description: Spec-driven development workflow. Use for exploring ideas, proposing changes, implementing specs, and archiving completed work. Triggers on "spec", "propose", "explore", "apply", "archive", "critique", or "specification".
version: 3.2.0
---

# Spec-Driven Development

For terminology and concepts, see [docs/concepts.md](../../docs/concepts.md).

## How This Works

Specs describe the system's behavior as a contract: what the system does (requirements) and how it behaves (scenarios). They live in `specs/reference/`, organized by capability. That's the source of truth.

When something needs to change, you create a **change** -- a folder under `specs/changes/` with artifacts that capture the intent, the behavioral modifications, and optionally the technical approach and implementation plan.

The **proposal** (`proposal.md`) is always the entry point. It answers *why* this change exists and names the capabilities affected. From there, artifacts can develop in the order that makes sense:

- **Spec Deltas** (`deltas/*/spec.md`) -- behavioral changes per capability (ADDED/MODIFIED/REMOVED/RENAMED requirements)
- **Design** (`design.md`) -- technical approach, when the how isn't obvious
- **Tasks** (`tasks.md`) -- implementation checklist, when the work has multiple steps

These artifacts aren't just a planning exercise. They make the change reviewable without reading code: the proposal explains why, the deltas show what's changing in the system's behavioral contract, and the design captures architectural decisions.

When implementation is complete and verified, the change is **archived**: deltas merge into the reference specs, the change moves to `changes/archive/`, and the reference reflects the new reality.

### When to Use SDD

**Use it for:** any code changes that reflect changed requirements or behavioral expectations.

**Skip it for:** simple bugfixes, routine refactors, dependency bumps, doc-only changes, exploratory spikes.

### File Ownership

| File | Owner | Others May Edit |
|------|-------|-----------------|
| `proposal.md` | Propose phase | With user confirmation |
| `deltas/*/spec.md` | Propose phase | With user confirmation |
| `design.md` | Propose phase | With user confirmation |
| `tasks.md` | Propose phase | Apply phase (checkboxes only) |
| `notes/*` | Any phase | Freely |

**Changing a spec may invalidate the design.** Always warn the user.

## Rules

1. **Specs are the source of truth.** Code serves specs. Never write specs to describe existing code -- that's backwards.
2. **`specs/` is for specs only.** No code files. `deltas/` contains only `spec.md` files. All code goes elsewhere.
3. **Don't fabricate.** Only document what was discussed or confirmed. No invented assumptions, no invented constraints. If unsure, ask.
4. **Prove your work.** Never claim "done" without passing tests or user verification. Walk through each requirement and scenario.
5. **Mark unknowns with `[CLARIFICATION NEEDED]`** and resolve them before proceeding.

**Don't:**
- Over-specify (specs guide, they don't pin down every detail)
- Design before scenarios are clear
- Add "might need" features -- only what's explicitly required
- Let specs go stale -- a spec that doesn't match the code is worse than no spec

## Commands

Each command maps to a phase. **Only read the reference doc for your current phase.**

| Command | What it does | Reference |
|---------|-------------|-----------|
| `/explore [topic]` | Investigate before committing to a proposal | [references/explore.md](references/explore.md) |
| `/propose [description]` | Create a change and its artifacts | [references/propose.md](references/propose.md) |
| `/refine [instruction]` | Update an existing artifact | Route to artifact reference below |
| `/apply [slug]` | Implement and verify a change | [references/apply.md](references/apply.md) |
| `/archive [slug]` | Merge deltas into reference, archive the change | [references/archive.md](references/archive.md) |

### Artifact References

When writing or refining an artifact, read its reference and use its template:

| Artifact | Reference | Template |
|----------|-----------|----------|
| `proposal.md` | [references/propose.md](references/propose.md) | `templates/proposal.md` |
| `deltas/*/spec.md` | [references/spec.md](references/spec.md) | `templates/spec-delta.md` |
| `design.md` | [references/design.md](references/design.md) | `templates/design.md` |
| `tasks.md` | [references/tasks.md](references/tasks.md) | `templates/tasks.md` |

### Refine Routing

`/refine` determines which artifact to update from the instruction:

- Context, motivation, scope → `proposal.md`
- Requirements, scenarios, behavior → relevant `spec.md` in `deltas/`
- Architecture, technical decisions → `design.md`
- Task breakdown, progress → `tasks.md`

If unclear, ask the user.

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

**Monorepo:** Each sub-project has its own `specs/` directory. `spectl` discovers them with `-r` (recursive). Use `--dir` to target a specific one.

## Interactive vs Autonomous

**Interactive** (default): Ask the user at each phase for input and confirmation (use AskUserQuestion tool).

**Autonomous** (when user requests it, e.g. "work on this until done"):

1. **Propose:** Draft all artifacts. Invoke **spec-critic** (`intra-spec` after proposal, `intra-spec` + `spec-code` after specs + design).
2. **Apply:** Implement and verify against all requirements and scenarios. Invoke **spec-critic** (`all`) before marking complete.
3. **Archive:** Invoke **spec-sync** → validate with **spec-critic** (`inter-spec`) → move to archive.

Only pause for genuine ambiguities or when the critic can't resolve after 5 rounds.

## Iteration

All phases can be revisited. `/refine` updates any existing artifact.

- Apply snag → may reveal a design flaw, spec gap, or proposal issue
- Changing a spec may invalidate the design -- always warn the user
- Scope changes require user confirmation in interactive mode; in autonomous mode, document in `notes/` and proceed

## Critique

The **spec-critic** agent (sonnet) provides adversarial review. See [references/critique.md](references/critique.md) for checklists.

| Mode | Checks |
|------|--------|
| `intra-spec` | Coherence within the spec |
| `spec-code` | Alignment with the codebase |
| `inter-spec` | Consistency across specs |
| `all` | All three |

**Verdicts:** `approved` | `approved-with-reservations` | `needs-work` | `blocked`

**Invocation:** "Consult with the spec-critic agent to review [spec path] (critique mode: [mode])"

**When `needs-work` or `blocked`:** Address concerns, resume the agent, repeat. Escalate to user after 5 rounds.

## Sub-Agents

| Agent | Role | Definition |
|-------|------|------------|
| **spec-critic** (sonnet) | Adversarial review of specs and implementation | `agents/spec-critic.md` |
| **spec-sync** (sonnet) | Merges deltas into reference specs during archive | `agents/spec-sync.md` |
