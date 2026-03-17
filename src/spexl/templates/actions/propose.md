# Propose Phase Reference

Create a new change and generate all artifacts in one flow: proposal → specs → design (optional) → tasks (optional).

## 1. Determine Specs Location

### Monorepo

In a monorepo, each sub-project has its own `specs/` directory next to its code. `spectl` discovers them with `-r` (recursive walk from the current directory). Use `--dir` to target a specific `specs/` directory explicitly.

No central config file is needed. Each `specs/` directory is self-contained with its own `reference/` and `changes/`.

## 2. Get Description and Create Directory

If no description was provided with the command, use AskUserQuestion:
- "What feature or capability are you specifying?"
- Keep it brief (2-5 words ideal)

Slugify the description:
- Lowercase, replace spaces with hyphens, remove special characters
- The slug names the *change*, not the capability being changed. It should describe what's being done: `add-oauth`, `fix-session-leak`, `refactor-auth-flow` -- not just `oauth` or `sessions`. A capability may be touched by many changes over time; the slug distinguishes *this* change.
- **Be precise and specific.** `add-spec-sync` is too vague if the deliverable is a subagent -- `spec-sync-subagent` is better. The slug should tell a reader exactly what the change produces without opening the proposal.
- Capability names live under `deltas/` and `reference/` and are a separate concern.

**Collision handling:** If the slug already exists in `specs/changes/`, ask user whether to continue the existing change or pick a different name.

## 3. Write Proposal

The first artifact is `proposal.md`. Use `templates/proposal.md`.

The template has four sections: **Why**, **What Changes**, **Capabilities**, **Impact**. Keep it concise (1-2 pages). Focus on the "why" not the "how" --implementation details belong in design.md.

The **Capabilities** section lists which features you're changing -- each one becomes a directory in `deltas/`. Check `specs/reference/` for existing capability names before filling in Modified Capabilities.

### Optional Sections

For larger or more complex changes, add any of these sections after **Why**:

- **Alternatives Considered** – Other approaches and why they were rejected
- **Constraints** – Technical limitations, business rules, dependencies
- **Assumptions** – Assumptions that must hold for this change to work
- **Stakeholders** – Who cares about this change and why
- **Out of Scope** – Explicitly excluded to prevent scope creep

These are not in the template by default. Add them when they carry real information.

## 4. Write Specs

After the proposal, proceed to per-capability spec deltas. Read [spec.md](spec.md) for notation and structure guidance.

One `spec.md` per capability listed in the proposal's Capabilities section, using `templates/spec-delta.md`.

## 5. Write Design (optional)

For features with multiple valid approaches or architectural decisions that need user input. Read [design.md](design.md) for guidance.

**Skip for:** simple features, bug fixes, obvious implementations.

## 6. Write Tasks (optional)

For changes with 3+ implementation steps or multi-session work. Read [tasks.md](tasks.md) for guidance. Use `templates/tasks.md`.

**Skip for:** simple specs where the spec itself is sufficient.

## Completion

All artifacts that make sense for the change should exist before moving to `/apply`.

**Interactive mode:** Inform user the change is ready for implementation.

**Autonomous mode:**
- After proposal → invoke **spec-critic** (`intra-spec`)
- After specs + design → invoke **spec-critic** (`intra-spec` + `spec-code`)
- Then proceed to apply

## Example Flows

**Single-project:**
```
User: /propose user authentication

1. Create: mkdir -p specs/changes/user-authentication
2. Write proposal.md (gather context, motivation, capabilities)
3. Write deltas/user-auth/spec.md (requirements, scenarios)
4. Write design.md (if non-trivial)
5. Write tasks.md (if multi-step)
```

**Monorepo:**
```
User: /propose login redesign (working in packages/web-app/)

1. specs/ exists at packages/web-app/specs/ (or use --dir)
2. Create: mkdir -p packages/web-app/specs/changes/login-redesign
3. Continue as above
```
