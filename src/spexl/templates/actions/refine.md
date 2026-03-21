# Refine Phase Reference

Update an existing artifact based on user instruction.

## Routing

Determine which artifact to update from the instruction:

- Context, motivation, scope → `proposal.md`
- Requirements, scenarios, behavior → relevant `spec.md` in `deltas/`
- Architecture, technical decisions → `design.md`
- Task breakdown, progress → `tasks.md`

If unclear, ask the user.

## Process

### 1. Load Context

Read the change directory to understand the current state:
- `proposal.md` for scope and motivation
- `deltas/*/spec.md` for current requirements
- `design.md` for technical decisions (if exists)
- `tasks.md` for progress (if exists)

### 2. Apply the Refinement

Follow the user's instruction. When updating:

- **Proposal:** Run `spexl context propose` for guidance on proposal structure.
- **Spec deltas:** Run `spexl context spec-notation` for notation guidance.
- **Design:** Run `spexl context design` for design guidance.
- **Tasks:** Run `spexl context tasks` for tasks guidance.

### 3. Check for Cascading Effects

**Changing a spec may invalidate the design.** Always warn the user.

- If a spec changes, check whether the design still makes sense
- If scope changes, check whether tasks need updating
- If the proposal changes, check whether specs still align

### 4. Confirm

**Interactive mode:** Show the user what changed and ask for confirmation.

**Autonomous mode:** Document the refinement in `notes/` and proceed.
