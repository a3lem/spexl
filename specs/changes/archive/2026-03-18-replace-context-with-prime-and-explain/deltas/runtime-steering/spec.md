## REMOVED Requirements

### Requirement: Context command
**Reason**: Replaced by two purpose-specific commands: `prime` (foundational knowledge via system prompt hook) and `explain` (advanced/niche knowledge on demand). The flat topic registry mixed information of fundamentally different scope and delivery needs.

## ADDED Requirements

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
