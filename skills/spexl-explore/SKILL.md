---
name: spexl-explore
description: Explore an idea, investigate a problem, or clarify requirements before committing to a formal spec change. Use when the user asks to "explore", "investigate", "think through", "research", "brainstorm", "understand the codebase", or wants a thinking partner before writing a proposal. Produces no artifacts by default -- this is discussion, diagrams, and code reading, not implementation. Transition to `/spexl-propose` when a decision crystallizes.
---

# Explore

Thinking-partner mode for exploring ideas and investigating problems before committing to a proposal.

## Load Methodology First

Before doing anything else, invoke the `spexl-foundations` skill. Tell it you're in the **explore** phase and need the rules, the big-picture concepts, and the spec directory layout. It will point you at the right references.

The methodology knowledge is needed so you can relate user questions to the spexl model -- for example, recognizing when something is a capability split vs a single capability change.

## Stance

- **Curious, not prescriptive.** Ask open questions, follow threads, challenge assumptions.
- **No implementation.** Read code, search the codebase, draw ASCII diagrams -- but do not write application code.
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

If the user says yes, transition to `/spexl-propose`. Pass along what you learned so the propose skill doesn't start from scratch.

## What Explore Is Not

- Not a workflow phase with required steps
- Not a gate before proposing (users can skip straight to `/spexl-propose`)
- Not implementation time (no code writing, no file creation outside `specs/`)

## Do Not

- Write code
- Create specs, proposals, or other change artifacts (wait for propose)
- Force a conclusion before the user is ready
- Invent assumptions the user hasn't confirmed -- when unsure, ask
