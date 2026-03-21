## ADDED Requirements

### Requirement: Computed status
The system SHALL compute a status for each active change based on which artifacts are present and the state of the task checklist. The `.change.json` file MAY contain a `skip` field listing artifacts that are intentionally omitted.

#### Scenario: All artifacts present, no tasks started
- **GIVEN** a change with proposal.md, design.md, tasks.md, and at least one delta spec
- **WHEN** no tasks are checked
- **THEN** the computed status is "ready"

#### Scenario: All artifacts present, some tasks done
- **GIVEN** a change with all artifacts present
- **WHEN** at least one task is checked and at least one is unchecked
- **THEN** the computed status is "in progress"

#### Scenario: All artifacts present, all tasks done
- **GIVEN** a change with all artifacts present
- **WHEN** all tasks are checked
- **THEN** the computed status is "complete"

#### Scenario: Missing artifact without skip
- **GIVEN** a change missing design.md or tasks.md
- **WHEN** the missing artifact is NOT listed in `.change.json` `skip`
- **THEN** the computed status is "drafting"

#### Scenario: Missing artifact with skip
- **GIVEN** a change missing design.md
- **WHEN** `.change.json` contains `"skip": ["design"]`
- **THEN** the status computation treats design as present
- **AND** the computed status advances past "drafting" if all other conditions are met

#### Scenario: Skip design and tasks
- **GIVEN** a change with only proposal.md and at least one delta spec
- **WHEN** `.change.json` contains `"skip": ["design", "tasks"]`
- **THEN** the computed status is "complete" (no task checklist to evaluate)

### Requirement: New command skip flag
The system SHALL support `spexl new <slug> --skip <artifact>` to write a skip list into `.change.json` at creation time. The flag can be repeated.

#### Scenario: New with skip
- **WHEN** the user runs `spexl new my-change --skip design --skip tasks`
- **THEN** `.change.json` contains `"skip": ["design", "tasks"]`

#### Scenario: New without skip
- **WHEN** the user runs `spexl new my-change` with no --skip flag
- **THEN** `.change.json` does not contain a `skip` field

### Requirement: Validate skip values
The system SHALL validate that the `skip` field in `.change.json` contains only `design` and/or `tasks`. Other values are invalid.

#### Scenario: Invalid skip value
- **GIVEN** a `.change.json` with `"skip": ["proposal"]`
- **WHEN** the user runs `spexl validate`
- **THEN** the system reports an error for the invalid skip value
- **AND** exits 1

#### Scenario: Valid skip value
- **GIVEN** a `.change.json` with `"skip": ["design"]`
- **WHEN** the user runs `spexl validate`
- **THEN** no skip-related errors are reported
