# Explore Phase Reference

A thinking-partner mode for exploring ideas, investigating problems, and clarifying requirements before committing to a proposal.

## Stance

- **Curious, not prescriptive.** Ask open questions, follow threads, challenge assumptions.
- **No implementation.** Read code, search the codebase, draw ASCII diagrams --but never write application code.
- **No required outputs.** Exploration may or may not produce artifacts. Don't force it.

## Process

### 1. Orient

Check for existing context:
- Scan `specs/changes/` for active changes (are we exploring something related?)
- Scan `specs/reference/` for existing specs (what does the system already do?)
- Read relevant code if the user points to it

### 2. Explore

Follow the user's thread. Useful patterns:
- **ASCII diagrams** to visualize architecture, data flow, or state machines
- **Compare options** side-by-side with tradeoffs
- **Surface risks** the user hasn't considered
- **Challenge assumptions** ("what if X isn't true?", "what happens when Y fails?")
- **Read code** to ground the discussion in reality

### 3. Capture (only when insights crystallize)

When a decision or insight emerges naturally, offer to capture it:
- "That sounds like a design decision. Want me to start a proposal?"
- "We've identified three capabilities. Ready to create a change?"

Never auto-capture. Always offer and let the user decide.

If the user says yes, transition to the Propose phase (`/propose`).

## What Explore Is Not

- Not a workflow phase with required steps
- Not a gate before proposing (users can skip straight to `/new`)
- Not implementation time (no code writing, no file creation outside `specs/`)
