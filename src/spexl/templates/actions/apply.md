# Apply Phase Reference

How to implement a proposed change, tracking progress and capturing learnings.

## Process

### 1. Load Context

Read the change directory:
- `proposal.md` - Why this change exists
- `deltas/*/spec.md` - What's changing (requirements and scenarios to satisfy)
- `tasks.md` - Progress overview (if exists)
- `design.md` - Technical approach (if exists)
- `notes/` - Previous learnings (if exists)

### 2. Determine Code Location

**Important:** The `deltas/` directory is for specification files only. All generated code must go elsewhere.

1. Check project structure for obvious code locations (e.g., `src/`, `lib/`, `app/`, project root)
2. Check `design.md` for specified file paths
3. If unclear, use AskUserQuestion: "Where should I place the generated code?"

Never write code files (`.js`, `.ts`, `.py`, `.html`, etc.) inside `deltas/*/`.

### 3. Implement

Work through the implementation:
- Follow the design decisions
- Satisfy each requirement and scenario from `deltas/*/spec.md`
- Update `tasks.md` checkboxes as tasks are completed (if exists)
- Track progress in notes if the work spans multiple sessions

### 4. Verify

Write tests alongside implementation -- not after. Spec scenarios translate directly to test cases. See [verification.md](verification.md) for test strategies, annotation conventions, and coverage expectations.

Every requirement needs at least one test. Every non-trivial scenario needs a corresponding test. Tests are annotated with `# spec:` comments linking back to the spec.

### 5. Capture Learnings (Optional)

Create or update `notes/` when there's new information worth recording. Notes can be created during any phase.

**Suggested note files:**
- `research.md` - Exploration findings, links, citations (any phase)
- `implementation.md` - Apply-phase learnings, gotchas, failed approaches

**What belongs in notes:**
- Learnings and gotchas discovered during implementation
- Research findings and explored files index
- Failed approaches and why they didn't work
- Context for future maintainers that isn't obvious from the code

**What does NOT belong in notes:**
- Restatements of proposal context (already in proposal.md)
- Restatements of scenarios (already in deltas/*/spec.md)
- Restatements of design decisions (already in design.md)

### 6. Complete

Before claiming completion:

1. **Run all tests** -- fix failures before proceeding
2. **Walk through each requirement** from `deltas/*/spec.md` and confirm a corresponding test exists
3. **If verification fails**, surface the choice: fix implementation, or adjust spec (needs user confirmation)

**Never claim "all scenarios satisfied" without passing tests.**

## Finding Specs

Specs are directories: `specs/changes/feature-name/`

When user references a spec by name, look for matching slugs in `specs/changes/*/`.

## Updating Specs

Only modify spec files in `deltas/` with user confirmation -- changes affect scope.
