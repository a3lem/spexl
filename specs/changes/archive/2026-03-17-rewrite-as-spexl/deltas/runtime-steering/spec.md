## ADDED Requirements

### Requirement: Context command
The system SHALL support `spexl context <topic>` to print relevant knowledge fragments to stdout. Topics map to composed content from `templates/partials/` and `templates/concepts/`.

#### Scenario: Context for an action
- **WHEN** the user runs `spexl context propose`
- **THEN** the system prints the shared rules (from partials), cross-phase warnings relevant to propose, and the propose-specific guidance (from actions)
- **AND** exits 0

#### Scenario: Context for a concept
- **WHEN** the user runs `spexl context concepts`
- **THEN** the system prints the full concepts document from `templates/concepts/concepts.md`
- **AND** exits 0

#### Scenario: Context for rules
- **WHEN** the user runs `spexl context rules`
- **THEN** the system prints the shared rules partial (specs are source of truth, don't fabricate, prove work, etc.)
- **AND** exits 0

#### Scenario: Context for structure
- **WHEN** the user runs `spexl context structure`
- **THEN** the system prints the directory structure conventions (specs/reference/, specs/changes/, artifact layout)
- **AND** exits 0

#### Scenario: Context for cross-phase
- **WHEN** the user runs `spexl context cross-phase`
- **THEN** the system prints cross-phase implications (changing a spec may invalidate design, apply snags may reveal proposal issues, etc.)
- **AND** exits 0

#### Scenario: Unknown topic
- **WHEN** the user runs `spexl context <unknown>`
- **THEN** the system prints an error listing available topics
- **AND** exits 1

#### Scenario: List available topics
- **WHEN** the user runs `spexl context --list`
- **THEN** the system prints all available topic names with one-line descriptions
- **AND** exits 0

### Requirement: Template command
The system SHALL support `spexl template <artifact-type>` to print an artifact template to stdout.

#### Scenario: Print proposal template
- **WHEN** the user runs `spexl template proposal`
- **THEN** the system prints the contents of `templates/artifacts/proposal.md` to stdout
- **AND** exits 0

#### Scenario: Print spec-delta template
- **WHEN** the user runs `spexl template spec-delta`
- **THEN** the system prints the contents of `templates/artifacts/spec-delta.md` to stdout
- **AND** exits 0

#### Scenario: Print design template
- **WHEN** the user runs `spexl template design`
- **THEN** the system prints the contents of `templates/artifacts/design.md`
- **AND** exits 0

#### Scenario: Print tasks template
- **WHEN** the user runs `spexl template tasks`
- **THEN** the system prints the contents of `templates/artifacts/tasks.md`
- **AND** exits 0

#### Scenario: Print reference-spec template
- **WHEN** the user runs `spexl template reference-spec`
- **THEN** the system prints the contents of `templates/artifacts/reference-spec.md`
- **AND** exits 0

#### Scenario: Unknown artifact type
- **WHEN** the user runs `spexl template <unknown>`
- **THEN** the system prints an error listing available artifact types
- **AND** exits 1

#### Scenario: List available templates
- **WHEN** the user runs `spexl template --list`
- **THEN** the system prints all available artifact type names
- **AND** exits 0
