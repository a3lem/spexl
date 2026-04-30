---
name: spexl-propose
description: Propose a new change in a spexl project. Use when the user asks to "propose a change", "create a spec", "start a new feature", "define requirements", "add a capability", "write a proposal", or describes new functionality that should be specified before implementation. Produces a change directory with proposal.md, per-capability spec deltas, and optionally design.md and tasks.md. Do not proceed to implementation from this skill -- that's the spexl-apply skill's job.
---

# Propose a Change

Create a new change under `specs/changes/<slug>/` and produce the artifacts that define it: proposal, spec deltas, and optionally design and tasks.

## Load Methodology First

Before doing anything else, invoke the `spexl-foundations` skill. Tell it you're in the **propose** phase and need the rules, spec notation, directory structure, design guidance, tasks guidance, and mode behavior. It will point you at the right references.

If you skip this step, you will get the notation wrong, produce invalid deltas, or violate rules the user expects. The methodology knowledge lives in that skill so this one doesn't have to carry it. Load it.

## Process

### 1. Locate the specs directory

In a single-project repo, `specs/` lives at the root. In a monorepo, each sub-project has its own `specs/` directory. `spexl changes -r` discovers them recursively. Use `spexl changes --dir <path>` to target a specific one.

If the user is working in a sub-project directory, the specs directory is usually that directory's `specs/`. If unclear, ask.

### 2. Determine the slug

If the user didn't provide a description, use AskUserQuestion: "What feature or capability are you specifying? (2-5 words)"

Slugify: lowercase, replace spaces with hyphens, remove special characters.

The slug names the **change**, not the capability. A capability may be touched by many changes over time; the slug distinguishes *this* change:

- Good: `add-oauth`, `fix-session-leak`, `refactor-auth-flow`, `spec-sync-subagent`
- Bad: `oauth`, `sessions`, `auth` -- these are capabilities, not changes
- Bad: `add-spec-sync` -- too vague if the deliverable is a subagent

Be precise. The slug should tell a reader exactly what the change produces without opening the proposal.

**Collision handling:** If `specs/changes/<slug>/` already exists, ask whether to continue the existing change or pick a different name.

### 3. Create the change directory

```
mkdir -p specs/changes/<slug>
```

Or use `spexl new <slug>` if you want the full scaffold.

### 4. Write the proposal

The first artifact is `proposal.md`. Four required sections:

```markdown
## Why

<1-2 sentences on the problem or opportunity.>

## What Changes

<Bullet list of concrete changes. Mark breaking changes with **BREAKING**.>

## Capabilities

### New Capabilities

- `capability-slug`: Brief description

### Modified Capabilities

- `capability-slug`: Brief description of what changes

## Impact

<Affected code, APIs, dependencies, or systems.>
```

Keep it concise (1-2 pages). Focus on *why*, not *how* -- implementation details belong in `design.md`.

Check `specs/reference/` for existing capability names before filling in **Modified Capabilities**. The Capabilities section drives the next step: each capability listed becomes a directory in `deltas/`.

**Optional sections** (add only when they carry real information):

- **Alternatives Considered** -- other approaches and why they were rejected
- **Constraints** -- technical limitations, business rules, dependencies
- **Assumptions** -- assumptions that must hold
- **Stakeholders** -- who cares and why
- **Out of Scope** -- explicit exclusions to prevent scope creep

### 5. Write per-capability spec deltas

For each capability listed in the proposal's **Capabilities** section, create `specs/changes/<slug>/deltas/<capability-slug>/spec.md`.

Follow the spec notation the `spexl-foundations` skill loaded for you:

- Title: `# [Capability Name]`
- Four possible sections: `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements`
- New capabilities: ADDED sections only
- Modified capabilities: MODIFIED (and optionally ADDED/REMOVED/RENAMED)
- Requirements as `### Requirement: <name>` with scenarios as `#### Scenario: <name>`

Use AskUserQuestion to understand behavior changes, acceptance criteria, and known constraints if you don't have enough to write requirements confidently.

After drafting each delta, walk through the validation checklist the methodology skill provided.

### 6. Write design.md (optional)

Follow the design guidance the methodology skill loaded. Skip for simple features, bug fixes, or obvious implementations.

If the change touches multiple modules, introduces a new pattern, or has security/performance/migration complexity, write it.

### 7. Write tasks.md (optional)

Follow the tasks guidance the methodology skill loaded. Skip for simple specs where the spec itself is sufficient.

If the change is 3+ implementation steps or multi-session work, write it. Include a Verification section with one task per requirement.

### 8. Hand off

All artifacts that make sense for this change should exist before moving to `/spexl-apply`. In autonomous mode, follow the propose workflow the methodology skill described (draft everything, invoke spexl-spec-critic, then proceed to apply).

**Interactive mode:** Tell the user the change is ready and suggest the next command: "Ready to implement. Invoke `/spexl-apply <slug>` when you want to start."

## Do Not

- Write code files inside `deltas/` -- only `spec.md` files live there
- Skip loading `spexl-foundations` -- you will get the notation wrong
- Invent constraints or assumptions the user didn't confirm -- mark unknowns with `[CLARIFICATION NEEDED]` instead
- Proceed to implementation -- that's a separate skill
