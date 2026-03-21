# Runtime Steering

## Overview / Purpose

Runtime steering commands serve knowledge on demand to AI agents during execution. The `explain` command prints advanced/niche knowledge for a given topic; the `template` command prints artifact templates by type. Both write to stdout for easy piping into agent context.

## Requirements

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

### Requirement: Explain command
The system SHALL support `spexl explain <topic>` to print advanced/niche knowledge on demand. Topics cover specific techniques and notation that an agent needs only when performing a particular subtask. The output is expository and human-readable, suitable for mid-conversation learning.

#### Scenario: Explain a topic
- **WHEN** the user runs `spexl explain spec-notation`
- **THEN** the system prints the spec notation and structure guide (requirement/scenario syntax, SHALL language, delta sections)
- **AND** exits 0

#### Scenario: Explain spexl methodology
- **WHEN** the user runs `spexl explain spexl`
- **THEN** the system prints the full SDD methodology overview (concepts, glossary, workflow) in expository narrative form, suitable for a reader learning the methodology
- **AND** exits 0

#### Scenario: Explain unknown topic
- **WHEN** the user runs `spexl explain <unknown>`
- **THEN** the system prints an error listing available topics
- **AND** exits 1

#### Scenario: List explain topics
- **WHEN** the user runs `spexl explain --list`
- **THEN** the system prints all available topic names with one-line descriptions
- **AND** exits 0
