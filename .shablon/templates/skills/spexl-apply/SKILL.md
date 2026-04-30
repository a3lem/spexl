---
name: spexl-apply
description: Implement a proposed spec change -- write the code and the tests that satisfy every requirement and scenario. Use when the user asks to "apply", "implement", "build the feature", "start coding the spec", "make it real", or references an active change that is ready for implementation. Never claim "done" without passing tests. Use `/spexl-archive` next to merge deltas into reference specs once the change is complete.
---

# Apply

Implement a proposed change: write the code, write the tests, and verify every requirement and scenario is satisfied.

## Load Methodology First

Before doing anything else, invoke the `spexl-foundations` skill. Tell it you're in the **apply** phase and need the rules, directory structure (especially file ownership of `deltas/`), verification guidance, and mode behavior. If autonomous mode or a critic invocation is in play, also ask for critique guidance.

## Process

### 1. Load change context

Read the change directory:

- `proposal.md` -- why this change exists
- `deltas/*/spec.md` -- what's changing; these are the requirements and scenarios to satisfy
- `design.md` -- technical approach (if exists)
- `tasks.md` -- progress overview (if exists)
- `notes/` -- previous learnings (if exists)

### 2. Determine code location

**Important:** The `deltas/` directory is for specification files only. All generated code must go elsewhere.

1. Check project structure for obvious code locations (`src/`, `lib/`, `app/`, project root)
2. Check `design.md` for specified file paths
3. If unclear, use AskUserQuestion: "Where should the generated code live?"

Never write `.py`, `.js`, `.ts`, `.html`, etc. inside `deltas/`.

### 3. Implement

Work through the change:

- Follow the design decisions
- Satisfy each requirement and scenario from `deltas/*/spec.md`
- Update `tasks.md` checkboxes as tasks complete (if `tasks.md` exists)
- Track progress in `notes/` if the work spans multiple sessions

### 4. Verify

Write tests alongside implementation -- not after. Spec scenarios translate directly to test cases.

- Every requirement needs at least one test
- Every non-trivial scenario needs a corresponding test
- Tests are annotated with `# spec:` comments linking back to the spec

Follow the verification guidance the methodology skill loaded for the annotation format, coverage check approach, and test strategy guidance (unit / behavioral / differential).

### 5. Capture learnings (optional)

Create or update `notes/` when there's new information worth recording. Notes can be created during any phase.

**Suggested note files:**

- `research.md` -- exploration findings, links, citations
- `implementation.md` -- apply-phase learnings, gotchas, failed approaches

**What belongs in notes:**

- Learnings and gotchas discovered during implementation
- Research findings and explored files index
- Failed approaches and why they didn't work
- Context for future maintainers that isn't obvious from the code

**What does NOT belong in notes:**

- Restatements of proposal context (already in `proposal.md`)
- Restatements of scenarios (already in `deltas/*/spec.md`)
- Restatements of design decisions (already in `design.md`)

### 6. Complete

Before claiming completion:

1. **Run all tests** -- fix failures before proceeding
2. **Walk through each requirement** from `deltas/*/spec.md` and confirm a corresponding test exists (use `spexl validate` if available, or grep for `# spec:` annotations and cross-reference)
3. **If verification fails**, surface the choice: fix the implementation, or adjust the spec (adjusting spec requires user confirmation and may cascade into design/tasks)

**Never claim "all scenarios satisfied" without passing tests.** This is rule 4.

**Autonomous mode:** Invoke `spexl-spec-critic` (`all`) before marking complete. Follow the mode behavior the methodology skill loaded.

## Updating Specs During Apply

If implementation reveals a gap in the spec, **do not silently update the spec**. Surface the choice: "The spec doesn't cover <case>. Do you want to refine the spec or work around it?" Spec changes require user confirmation because they affect scope.

## Next Step

When the change is complete and all tests pass, suggest: "Ready to archive. Invoke `/spexl-archive <slug>` to merge deltas into the reference specs."

## Do Not

- Write code inside `deltas/`
- Claim "done" without running tests
- Silently modify spec deltas to match what you actually built
- Skip writing tests for requirements that "seem obvious"
- Proceed to archive -- that's a separate skill
