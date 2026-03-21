## ADDED Requirements

### Requirement: Prime command
The system SHALL support `spexl prime` to print foundational spexl knowledge formatted for system prompt injection. The output is agent-facing: concise, imperative, and structured for machine consumption.

#### Scenario: Prime output
- **WHEN** the user runs `spexl prime`
- **THEN** the system prints spexl's foundational methodology (reference specs vs spec deltas, the change lifecycle, the archive model, key terminology, directory structure conventions) formatted as imperative instructions suitable for a system prompt
- **AND** the output does NOT include phase-specific instructions, artifact writing guidance, or critique checklists
- **AND** exits 0
