---
name: spexl-refine
description: Update an existing artifact in a spexl change. Use when the user asks to "refine", "update the proposal", "modify the spec", "change requirements", "revise the design", "update tasks", or has feedback that changes scope, behavior, approach, or task breakdown of an active change. Routes the refinement to the right file (proposal, spec delta, design, or tasks) and warns about cascading effects. Use `/spexl-propose` instead if the user wants to start a new change.
---

# Refine

Update an existing artifact based on user instruction. Route the change to the correct file and surface cascading effects.

## Load Methodology First

Before doing anything else, invoke the `spexl-foundations` skill. Tell it you're in the **refine** phase and need the rules, file ownership, and mode behavior. Ask for additional guidance based on which artifact the refinement touches:

- Spec delta → ask for spec notation
- `design.md` → ask for design guidance
- `tasks.md` → ask for tasks guidance

## Routing

Determine which artifact to update from the instruction:

| Instruction touches... | Edit... |
|------------------------|---------|
| Context, motivation, scope | `proposal.md` |
| Requirements, scenarios, behavior | relevant `deltas/*/spec.md` |
| Architecture, technical decisions | `design.md` |
| Task breakdown, progress | `tasks.md` |

If unclear, ask the user.

## Process

### 1. Locate the change

If the user named a slug, confirm `specs/changes/<slug>/` exists. If not, offer `spexl changes` or ask for the right slug.

If they didn't name one, list active changes (`spexl changes`) and ask which.

### 2. Load context

Read the change directory to understand the current state:

- `proposal.md` -- scope and motivation
- `deltas/*/spec.md` -- current requirements
- `design.md` -- technical decisions (if exists)
- `tasks.md` -- progress (if exists)
- `notes/` -- prior learnings (if exists)

### 3. Apply the refinement

Follow the user's instruction. Consult the appropriate guidance that `spexl-foundations` provided:

- **Proposal** changes: preserve the four required sections (Why, What Changes, Capabilities, Impact). Update Capabilities if the scope shifts.
- **Spec deltas**: follow the notation and structure the methodology skill loaded. Remember MODIFIED blocks must include the full requirement (all scenarios, even unchanged), because the merge replaces the entire block.
- **Design**: follow the design guidance the methodology skill loaded.
- **Tasks**: follow the tasks guidance the methodology skill loaded. Only restructure if the scope itself changed.

### 4. Check for cascading effects

A refinement in one artifact often invalidates another. Walk through these and warn the user if any apply:

- **Spec changed** → design may no longer cover all scenarios
- **Scope changed in proposal** → deltas and tasks may need updating; capabilities in proposal may need edits
- **Design changed** → implementation may need adjusting (if already applied)
- **Capability added/removed in proposal** → `deltas/` directory list needs to match

Don't silently fix cascades. Surface them. The user decides what gets updated.

### 5. Confirm

**Interactive mode:** Show the user what changed and ask for confirmation. If cascades were surfaced, ask whether to follow up on any.

**Autonomous mode:** Document the refinement in `notes/refinement.md` (date-stamped entry) and proceed. Invoke spexl-spec-critic if the refinement was substantive. Follow the mode behavior the methodology skill loaded.

## Do Not

- Restructure tasks mid-execution unless the scope actually changed
- Rewrite a MODIFIED spec block without including all scenarios
- Silently cascade changes across files -- always name them and let the user decide
- Invent refinements beyond what the user asked for
