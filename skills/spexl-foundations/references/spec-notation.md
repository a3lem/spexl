# Spec Notation

Specs support three notations. Mix them freely within a single spec.

## SHALL Statements

Use SHALL for requirements, constraints, and non-functional requirements. Follows EARS (Easy Approach to Requirements Syntax) qualifiers.

| Pattern | Use When |
|---------|----------|
| The system SHALL [action] | Unconditional requirement |
| WHEN [trigger], the system SHALL [action] | Event-driven requirement |
| IF [condition], the system SHALL [action] | State-dependent requirement (positive) |
| IF [unwanted condition], the system SHALL [mitigation] | Unwanted behavior handling |
| WHILE [state], the system SHALL [action] | Ongoing constraint |
| WHILE [state] WHEN [trigger], the system SHALL [action] | Complex/compound requirement |
| WHERE [feature is included], the system SHALL [action] | Optional/product-line feature |

**Examples:**

- The system SHALL encrypt all data at rest using AES-256.
- WHEN a user exceeds 5 failed login attempts, the system SHALL lock the account for 15 minutes.
- IF the database is unreachable, the system SHALL retry 3 times with exponential backoff.
- IF a payment fails due to insufficient funds, the system SHALL notify the user and cancel the order.
- WHILE the system is in maintenance mode, the system SHALL return 503 for all API requests.
- WHILE the system is rate-limited WHEN a new request arrives, the system SHALL queue the request and return 429.
- WHERE the audit-logging module is enabled, the system SHALL record all write operations to the audit log.

## Given/When/Then Scenarios

Use Given/When/Then for behavioral specs that map directly to tests.

```
Scenario: User logs in with valid credentials
  Given a registered user with email "user@example.com"
  When the user submits valid credentials
  Then the system returns an authentication token
  And the token expires in 24 hours

Scenario: User logs in with invalid password
  Given a registered user with email "user@example.com"
  When the user submits an invalid password
  Then the system returns a 401 error
  And no token is issued
```

| Keyword | Purpose |
|---------|---------|
| **Given** | Precondition -- system state before the action |
| **When** | Action -- what the user or system does |
| **Then** | Outcome -- observable result |
| **And** | Continuation of previous keyword |
| **But** | Negative continuation (e.g., "But no email is sent") |

## Plain Prose

Use plain prose where formal notation adds no value -- overviews, context, migration notes, explanations.

## Choosing Notation

| Content | Recommended Notation |
|---------|---------------------|
| Functional requirements | SHALL statements |
| Constraints and NFRs | SHALL statements |
| Behavioral acceptance criteria | Given/When/Then scenarios |
| Test-mappable specifications | Given/When/Then scenarios |
| Context, overviews, migration notes | Plain prose |
| Complex multi-step interactions | Given/When/Then scenarios |

A single requirement often benefits from both: a SHALL statement declaring the rule, followed by a scenario demonstrating it.

### Hybrid Example

```
### Requirement: Session Timeout
The system SHALL expire sessions after 30 minutes of inactivity.

#### Scenario: Idle timeout
  Given an authenticated session
  When 30 minutes pass without activity
  Then the session is invalidated

#### Scenario: Activity resets timeout
  Given an authenticated session
  When the user performs an action at minute 29
  Then the session timeout resets to 30 minutes
```

## Writing Guidelines

- Write scenarios in third person, present tense
- One scenario per behavior -- don't combine happy path and error in one
- Use concrete values: "2 seconds" not "quickly", "3 retries" not "a few times"
- Avoid: might, should, could, usually → Use: specific outcomes

## Spec Delta Structure

A delta spec lives at `specs/changes/<slug>/deltas/<capability>/spec.md` and contains up to four section types:

- `## ADDED Requirements` -- new behavior (appended to reference on archive)
- `## MODIFIED Requirements` -- changed behavior (replaces matching block on archive)
- `## REMOVED Requirements` -- deprecated behavior (deleted on archive)
- `## RENAMED Requirements` -- name change only (heading updated on archive)

**Template guidance:**

- Title: `# [Capability Name]`
- Requirements as `### Requirement: <name>` with scenarios as `#### Scenario: <name>`
- MODIFIED must include the complete requirement block -- all scenarios, even unchanged ones. The requirement heading is the match key; the entire block (SHALL statement + every scenario) is replaced at merge time. Do not omit unchanged scenarios or use partial diffs.
- REMOVED must include **Reason** and **Migration** fields
- RENAMED uses `### FROM: <old>` / `### TO: <new>` format
- Each scenario should test ONE behavior
- Use concrete values in examples, not placeholders
- Delete sections that don't apply

## Reference Spec Structure

A reference spec lives at `specs/reference/<capability>/spec.md` and typically contains:

- `# [Capability Name]`
- `## Overview` -- plain prose context
- `## Requirements` -- SHALL statements, optionally with Given/When/Then scenarios nested under each
- `## Non-Functional Requirements` -- performance, security, compliance (optional)
- `## Glossary` -- capability-specific terms (optional)

No ADDED/MODIFIED/REMOVED/RENAMED headers. Reference specs describe current behavior, not how it changed.

## Validation Checklist

Review a spec (reference or delta) against this checklist:

**Completeness:**

- [ ] Happy path scenarios documented
- [ ] Error/edge case scenarios documented
- [ ] Boundary conditions covered

**Clarity:**

- [ ] Each scenario tests one behavior
- [ ] Concrete values used (no vague terms)
- [ ] SHALL statements use EARS qualifiers correctly
- [ ] Given/When/Then structure consistent where used

**Consistency:**

- [ ] Terminology consistent across requirements and scenarios
- [ ] No contradictory requirements or scenarios
- [ ] ADDED/MODIFIED/REMOVED/RENAMED sections accurate (for spec deltas)
- [ ] Each capability directory in `deltas/` corresponds to an entry in the proposal's Capabilities section

**Testability:**

- [ ] Each requirement or scenario is directly verifiable
- [ ] Outcomes are observable
- [ ] No untestable assertions

## Cross-Cutting Changes

Some changes touch many capabilities at once (e.g., "add audit logging to all write operations"). This means one delta per capability, each with similar ADDED/MODIFIED sections.

- This is expected. The per-capability structure ensures each reference spec stays accurate after archive merge.
- Group related deltas by naming them consistently within the proposal's Capabilities section.
- Use the proposal to explain the cross-cutting nature.
- If the change is truly identical across capabilities, note "Same pattern as [capability]" in the delta to reduce duplication while keeping each file self-contained.
