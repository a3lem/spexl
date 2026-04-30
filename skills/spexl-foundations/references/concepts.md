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

A spec is a behavioral contract. It states what the system does using requirements and scenarios.

```markdown
### Requirement: Session Timeout
The system SHALL expire sessions after 30 minutes of inactivity.

#### Scenario: Idle timeout
  Given an authenticated session
  When 30 minutes pass without activity
  Then the session is invalidated
```

Requirements use SHALL statements (from requirements engineering). Scenarios use Given/When/Then (from BDD). The combination gives precision and testability.

### Requirements and Scenarios

A **requirement** declares a rule: what the system must do. It uses SHALL with EARS qualifiers (WHEN, IF, WHILE, WHERE) to state the condition and the expected behavior.

A **scenario** is a concrete example of a requirement in action. It sets up a specific situation (Given), performs an action (When), and asserts an observable outcome (Then). Where a requirement says "the system SHALL do X," a scenario says "in *this* situation, here's what X looks like." Scenarios map directly to tests.

Requirements without scenarios are unverifiable. Scenarios without requirements lack context. Together, they form a testable contract: the requirement states the rule, the scenario proves it holds.

Each scenario should test one behavior, use concrete values ("30 minutes" not "a period of time"), and produce an observable outcome. A requirement typically has multiple scenarios covering the happy path, error cases, and boundary conditions.

A spec lives in `spec.md` and serves double duty:

- In `reference/`: describes what *is* built
- In `deltas/`: describes what *is to be* built

This is why they're called specs, not requirements. A requirement implies something yet to be fulfilled. A spec works in both tenses.

### Capabilities

Specs are organized by capability -- a logical grouping of related behavior.

```
reference/
├── authentication/
│   └── spec.md
├── billing/
│   └── spec.md
└── notifications/
    └── spec.md
```

A capability is a domain concept, not a code module. `authentication` might touch controllers, middleware, database models, and background jobs. The spec describes the behavior; design and code decide where it lives.

## Changes

A change is a proposed modification to the system. It lives in a folder under `changes/` and contains everything needed to understand, review, and implement the modification.

```
changes/add-oauth/
├── proposal.md          Why this change exists
├── deltas/              What's changing (per-capability)
│   ├── authentication/
│   │   └── spec.md
│   └── session-management/
│       └── spec.md
├── design.md            How to implement it (optional)
├── tasks.md             Steps to take (optional)
└── notes/               Learnings along the way (optional)
```

Changes are identified by slug. The slug names the change, not the capability: `add-oauth`, not `authentication`. A capability may be touched by many changes over time.

Multiple changes can coexist without conflict. Each is self-contained.

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

A spec delta describes what's changing in a single capability, relative to the current reference spec (or from scratch, if the capability is new).

```markdown
## ADDED Requirements

### Requirement: OAuth Login
The system SHALL support OAuth 2.0 login via Google and GitHub.

#### Scenario: Google OAuth
  Given a user with a Google account
  When they initiate "Sign in with Google"
  Then they are authenticated via OAuth 2.0

## MODIFIED Requirements

### Requirement: Session Timeout
The system SHALL expire sessions after 60 minutes of inactivity.

#### Scenario: Idle timeout
  Given an authenticated session
  When 60 minutes pass without activity
  Then the session is invalidated

## REMOVED Requirements

### Requirement: Legacy Auth
**Reason**: Replaced by OAuth
**Migration**: Users must re-register with OAuth provider
```

Four section types:

| Section | Meaning | On archive |
|---------|---------|------------|
| `ADDED` | New behavior | Appended to reference spec |
| `MODIFIED` | Changed behavior (full replacement) | Replaces matching requirement |
| `REMOVED` | Deprecated behavior | Deleted from reference spec |
| `RENAMED` | Name change only | Heading updated in reference spec |

MODIFIED provides the complete requirement block -- SHALL statement and all scenarios, even unchanged ones. The requirement heading is the match key; the entire block is replaced at merge time. This keeps each delta self-contained and the merge mechanical: find block, replace block. No partial diffs, no scenario-level operations, no "intelligent" merging.

### Why Deltas

**Clarity.** A delta shows exactly what's changing. No mental diffing against the full spec.

**Parallel work.** Two changes can touch the same capability without conflicting, as long as they modify different requirements.

**Brownfield fit.** Most work modifies existing behavior. Deltas make modifications first-class.

## Archive

Archiving completes a change. Its spec deltas merge into the reference, and the change folder moves to `changes/archive/` with a date prefix.

```
Before:
  reference/auth/spec.md          ◄── current behavior
  changes/add-oauth/deltas/auth/  ─── proposed changes

After:
  reference/auth/spec.md          ◄── now includes OAuth
  changes/archive/2026-03-16-add-oauth/  ◄── preserved history
```

Reference specs describe how things work *now*, not how they changed. The archived change preserves the full story: the proposal (why), the deltas (what changed), the design (how), and the tasks (what was done).

**The cycle:**

1. Reference specs describe current behavior
2. A change proposes modifications as deltas
3. Implementation makes the changes real
4. Archive merges deltas into the reference
5. Reference specs describe the new behavior
6. Next change builds on the updated reference

## Verification

Every requirement needs a test. Every non-trivial scenario needs a corresponding test. Tests link back to specs with annotations:

```python
# spec: session-management requirement=session-timeout scenario=idle-timeout
def test_idle_timeout():
    ...
```

A change is not complete until all requirements have passing tests. Claiming "done" without evidence is an anti-pattern.

## Critique

The spexl-spec-critic agent provides adversarial review -- a skeptical senior engineer who demands proof that the work is sound.

Three modes:

| Mode | Checks |
|------|--------|
| `intra-spec` | Coherence within the spec (contradictions, ambiguity, coverage) |
| `spec-code` | Alignment with the codebase (assumptions validated, conventions followed) |
| `inter-spec` | Consistency across specs (no conflicts between active changes) |

The critic returns a verdict: `approved`, `approved-with-reservations`, `needs-work`, or `blocked`. Multi-turn dialogue continues until concerns are addressed or escalated to the user.

## Glossary

| Term | Definition |
|------|------------|
| **Artifact** | A document within a change (proposal, spec, design, tasks, or notes) |
| **Archive** | Completing a change by merging deltas into reference and preserving history |
| **Capability** | A logical grouping of related behavior (e.g., `authentication`, `billing`) |
| **Change** | A proposed modification to the system, packaged as a folder with artifacts |
| **Critique** | Adversarial review of specs and implementation by the spexl-spec-critic agent |
| **Spec delta** | A spec describing changes (ADDED/MODIFIED/REMOVED/RENAMED) relative to the reference spec |
| **Reference spec** | The source of truth for a capability's current behavior |
| **Requirement** | A rule the system must follow, stated as a SHALL statement with EARS qualifiers |
| **Scenario** | A concrete example of a requirement in action: a specific situation, action, and observable outcome |
| **Slug** | The kebab-case directory name identifying a change |
| **Spec** | A behavioral contract: what the system does (requirements) and how it behaves (scenarios) |
