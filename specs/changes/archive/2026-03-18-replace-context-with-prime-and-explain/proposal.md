## Why

The current `context` command bundles topics of wildly different scope and purpose into one flat registry. Phase instructions, methodology concepts, spec notation guides, and agent checklists all live behind the same `spexl context <topic>` interface. This makes it hard to compose the right information at the right time, and creates a duplication problem: skills bake in shared knowledge that `context` also serves.

A three-level knowledge architecture resolves this. Foundational knowledge (what spexl is, how specs work) gets injected once via a system prompt hook. Operational knowledge (how to run a specific phase) lives directly in each skill. Advanced/niche knowledge (spec notation, testing strategies, critique checklists) is available on demand via an `explain` command. Each level has a delivery mechanism matched to its lifecycle.

## What Changes

- **New `prime` command** – outputs foundational spexl knowledge formatted for system prompt injection. Used by a SessionStart hook, not by skills.
- **New `explain` command** – replaces `context` for on-demand knowledge delivery. `spexl explain <topic>` serves advanced/niche topics. `spexl explain spexl` serves the full methodology overview (overlaps with `prime` content but expository rather than imperative).
- **`context` command removed** – replaced entirely by `prime` + `explain`.
- **`template` command unchanged** – stays as-is for scaffolding needs (subagents, non-Claude workflows, manual use).

## Capabilities

### New Capabilities

- `knowledge-priming`: The `prime` command for system prompt injection of foundational knowledge

### Modified Capabilities

- `runtime-steering`: The `context` requirement is replaced by `explain`; `template` requirement unchanged

## Impact

- `src/spexl/cli/steering.py` – `context` implementation replaced by `prime` and `explain`
- `src/spexl/__init__.py` – CLI routing updated for new commands
- `TOPIC_REGISTRY` – split into `EXPLAIN_REGISTRY` (Level 3 topics) and prime content (Level 1)
- `src/spexl/templates/` – content reorganized by level; partials may need reclassification
- Skill generation (future change) – will need to account for Level 1 being in the system prompt, not in skills
- Tests – existing `context` tests replaced by `prime` and `explain` tests
