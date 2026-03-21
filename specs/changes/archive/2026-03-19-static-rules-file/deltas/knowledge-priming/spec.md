## MODIFIED Requirements

### Requirement: Prime command
The system SHALL support `spexl prime` to print foundational spexl knowledge formatted for system prompt injection. The output is agent-facing: concise, imperative, and structured for machine consumption. The output of this command is persisted as `.claude/rules/spexl.md` by `spexl init` and `spexl update`.

#### Scenario: Prime output
- **WHEN** the user runs `spexl prime`
- **THEN** the system prints spexl's foundational methodology formatted as imperative instructions suitable for a system prompt, covering:
  - Core model (reference specs vs spec deltas, the change lifecycle, the archive model)
  - Key terminology and directory structure conventions
  - Workflow phases and their corresponding skills (slash commands)
  - Sub-agents (spec-critic, spec-sync) with roles and modes
  - CLI quick reference (plumbing, steering, skill generation commands)
- **AND** the output does NOT include phase-specific procedural instructions, artifact writing guidance, or full critique checklists
- **AND** exits 0
