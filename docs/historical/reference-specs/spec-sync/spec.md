# Spec Sync

## Overview

Subagent that merges delta specs into reference specs during the archive phase. Handles ADDED, MODIFIED, REMOVED, and RENAMED operations across all capabilities in a change. The merge is mechanical: operators identify requirements by heading, and each operation applies to the entire requirement block (SHALL statement + all scenarios). No scenario-level operations.

## Requirements

### Requirement: Delta-to-reference merge

The spec-sync agent SHALL merge each delta spec in a change's `deltas/` directory into the corresponding reference spec.

#### Scenario: ADDED requirements
  Given a delta spec at `deltas/user-auth/spec.md` with an ADDED section containing "Requirement: OAuth Login"
  And a reference spec exists at `specs/reference/user-auth/spec.md`
  When the spec-sync agent processes the delta
  Then "### Requirement: OAuth Login" and its scenarios are appended to the reference spec's "## Scenarios" section
  And the "## ADDED Requirements" header is not included in the reference spec

#### Scenario: MODIFIED requirements
  Given a delta spec with a MODIFIED section for "Requirement: Session Timeout"
  And the reference spec contains a "### Requirement: Session Timeout" block
  When the spec-sync agent processes the delta
  Then the entire "### Requirement: Session Timeout" block in the reference spec is replaced with the delta's version

#### Scenario: REMOVED requirements
  Given a delta spec with a REMOVED section for "Requirement: Legacy Auth"
  And the reference spec contains a "### Requirement: Legacy Auth" block
  When the spec-sync agent processes the delta
  Then the "### Requirement: Legacy Auth" block is deleted from the reference spec

#### Scenario: RENAMED requirements
  Given a delta spec with a RENAMED section mapping "Basic Auth" to "Password Auth"
  And the reference spec contains "### Requirement: Basic Auth"
  When the spec-sync agent processes the delta
  Then the heading is updated to "### Requirement: Password Auth"
  And the block content is preserved

#### Scenario: New capability (no existing reference)
  Given a delta spec at `deltas/oauth-provider/spec.md` with only ADDED sections
  And no reference spec exists at `specs/reference/oauth-provider/`
  When the spec-sync agent processes the delta
  Then `specs/reference/oauth-provider/spec.md` is created using `templates/reference-spec.md`
  And the ADDED requirements are placed under "## Scenarios"

### Requirement: Error handling

The spec-sync agent SHALL handle mismatches between delta operations and reference spec state gracefully.

#### Scenario: MODIFIED targets nonexistent requirement
  Given a delta spec with a MODIFIED section for "Requirement: Session Timeout"
  And the reference spec does not contain a "### Requirement: Session Timeout" block
  When the spec-sync agent processes the delta
  Then it treats the MODIFIED requirement as an ADDED requirement and appends it to the reference spec

#### Scenario: REMOVED targets nonexistent requirement
  Given a delta spec with a REMOVED section for "Requirement: Legacy Auth"
  And the reference spec does not contain a "### Requirement: Legacy Auth" block
  When the spec-sync agent processes the delta
  Then it skips the removal silently (the requirement is already absent)

#### Scenario: RENAMED targets nonexistent requirement
  Given a delta spec with a RENAMED section mapping "Basic Auth" to "Password Auth"
  And the reference spec does not contain "### Requirement: Basic Auth"
  When the spec-sync agent processes the delta
  Then it uses AskUserQuestion to ask the user how to proceed

#### Scenario: Malformed delta spec
  Given a delta spec with unrecognizable section structure
  When the spec-sync agent attempts to parse it
  Then it uses AskUserQuestion to surface the problem and ask for guidance

### Requirement: Reference spec cleanliness

The spec-sync agent SHALL ensure merged reference specs contain no delta markers. Reference specs describe current behavior, not how it changed.

#### Scenario: No delta section headers in output
  Given a delta with "## ADDED Requirements", "## MODIFIED Requirements", and "## REMOVED Requirements" sections
  When the spec-sync agent completes the merge
  Then none of these section headers appear in the reference spec

#### Scenario: Removed requirements leave no trace
  Given a REMOVED requirement "Legacy Auth" in the delta
  When the spec-sync agent completes the merge
  Then neither "### Requirement: Legacy Auth" nor the REMOVED reason/migration fields appear in the reference spec

### Requirement: Multi-capability sync

The spec-sync agent SHALL process all delta specs in a change's `deltas/` directory in a single invocation.

#### Scenario: Multiple deltas
  Given a change with deltas for `user-auth` and `session-management`
  When the spec-sync agent is invoked for the change
  Then both `specs/reference/user-auth/spec.md` and `specs/reference/session-management/spec.md` are updated

#### Scenario: Mixed new and existing capabilities
  Given a change with a delta for existing capability `user-auth` and new capability `oauth-provider`
  When the spec-sync agent is invoked
  Then `specs/reference/user-auth/spec.md` is updated in place
  And `specs/reference/oauth-provider/spec.md` is created

### Requirement: Invocation interface

The spec-sync agent SHALL be invocable by the main agent via the Agent tool during the `/archive` flow.

#### Scenario: Invocation by main agent
  Given the user runs `/archive add-oauth`
  When the main agent reaches the sync step
  Then it invokes the spec-sync agent with the change directory path

#### Scenario: Invocation context
  When the spec-sync agent is invoked
  Then it receives the change directory path as input
  And it reads `deltas/*/spec.md` to determine which reference specs to update
  And it reads `specs/reference/` to find existing reference specs

