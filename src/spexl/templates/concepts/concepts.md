# Concepts

## The Big Idea

Specifications are the source of truth. Code serves specs, not the other way around.

```
specs/
├── reference/          Source of truth: how the system works now
└── changes/            Proposed modifications, each in its own folder
```

**Reference specs** describe current behavior. **Changes** propose modifications as deltas against the reference. When a change is complete, its deltas merge into the reference, and the reference reflects the new reality. Next change builds on the updated reference.

```
reference describes behavior
       ▲
       │ archive merges deltas
       │
change proposes modification
       │
       ▼
implementation makes it real
```

## Specs

A spec is a behavioral contract. It states what the system does using **requirements** (SHALL statements with EARS qualifiers) and **scenarios** (Given/When/Then). Requirements declare rules; scenarios prove the rules hold with concrete examples. Together they form a testable contract. Scenarios map directly to tests.

A spec lives in `spec.md` and serves double duty: in `reference/` it describes what *is* built, in `deltas/` it describes what *is to be* built. This is why they're called specs, not requirements -- a spec works in both tenses.

For notation details (SHALL/EARS patterns, Given/When/Then structure, choosing notation), run `spexl explain spec-notation`.

### Capabilities

Specs are organized by capability -- a logical grouping of related behavior (e.g., `authentication`, `billing`). A capability is a domain concept, not a code module. The spec describes the behavior; design and code decide where it lives.

## Changes

A change is a proposed modification to the system. It lives in a folder under `changes/` and contains everything needed to understand, review, and implement the modification. Changes are identified by slug. The slug names the change, not the capability: `add-oauth`, not `authentication`. A capability may be touched by many changes over time. Multiple changes can coexist without conflict.

## Artifacts

Artifacts are the documents within a change. Each serves a distinct purpose.

```
proposal ──► specs ──► design ──► tasks ──► implement
   why        what       how      steps
```

| Artifact | Purpose | Required |
|----------|---------|----------|
| `proposal.md` | Why this change, what it affects, which capabilities | Yes |
| `deltas/*/spec.md` | Behavioral contract per affected capability | Yes |
| `design.md` | Technical approach, architecture decisions | When non-trivial |
| `tasks.md` | Implementation checklist with progress tracking | When multi-step |
| `notes/*` | Learnings, research, failed approaches | Freely |

Artifacts build on each other. The proposal names the capabilities; specs define the behavioral changes per capability; design explains how to implement them; tasks break the work into steps.

## Spec Deltas

A spec delta describes what's changing in a single capability, relative to the current reference spec (or from scratch, if the capability is new). Four operation types: ADDED (new behavior), MODIFIED (changed behavior -- full replacement), REMOVED (deprecated behavior), RENAMED (heading change only). On archive, each operation merges mechanically into the reference spec.

MODIFIED provides the complete requirement block -- SHALL statement and all scenarios, even unchanged ones. The requirement heading is the match key; the entire block is replaced. No partial diffs, no "intelligent" merging.

For the full delta template and writing guidance, run `spexl explain spec-notation`.

### Why Deltas

**Clarity.** A delta shows exactly what's changing. No mental diffing against the full spec.

**Parallel work.** Two changes can touch the same capability without conflicting, as long as they modify different requirements.

**Brownfield fit.** Most work modifies existing behavior. Deltas make modifications first-class.

## Archive

Archiving completes a change. Its spec deltas merge into the reference, and the change folder moves to `changes/archive/` with a date prefix. Reference specs describe how things work *now*, not how they changed. The archived change preserves the full story.

**The cycle:**

1. Reference specs describe current behavior
2. A change proposes modifications as deltas
3. Implementation makes the changes real
4. Archive merges deltas into the reference
5. Reference specs describe the new behavior
6. Next change builds on the updated reference

## Verification

Every requirement needs a test. Every non-trivial scenario needs a corresponding test. A change is not complete until all requirements have passing tests. For test strategies, annotation conventions, and coverage expectations, run `spexl explain verification`.

## Critique

The spec-critic agent provides adversarial review -- three modes: `intra-spec` (coherence), `spec-code` (code alignment), `inter-spec` (cross-spec consistency). Returns a verdict (`approved`, `approved-with-reservations`, `needs-work`, `blocked`) and engages in multi-turn dialogue until concerns are resolved. For checklists and dialogue rules, run `spexl explain critique`.

## Glossary

| Term | Definition |
|------|------------|
| **Artifact** | A document within a change (proposal, spec, design, tasks, or notes) |
| **Archive** | Completing a change by merging deltas into reference and preserving history |
| **Capability** | A logical grouping of related behavior (e.g., `authentication`, `billing`) |
| **Change** | A proposed modification to the system, packaged as a folder with artifacts |
| **Critique** | Adversarial review of specs and implementation by the spec-critic agent |
| **Spec delta** | A spec describing changes (ADDED/MODIFIED/REMOVED/RENAMED) relative to the reference spec |
| **Reference spec** | The source of truth for a capability's current behavior |
| **Requirement** | A rule the system must follow, stated as a SHALL statement with EARS qualifiers |
| **Scenario** | A concrete example of a requirement in action: a specific situation, action, and observable outcome |
| **Slug** | The kebab-case directory name identifying a change |
| **Spec** | A behavioral contract: what the system does (requirements) and how it behaves (scenarios) |
