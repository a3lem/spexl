## MODIFIED Requirements

### Requirement: Init target
The system SHALL support `spexl init claude` as an interactive command to set up spexl in a Claude Code project. It installs skills, agents, a SessionStart hook, and scaffolds the `specs/` directory.

#### Scenario: Interactive setup flow
- **WHEN** the user runs `spexl init claude`
- **THEN** the system searches up the directory tree for an existing `.claude/` directory or `CLAUDE.md`
- **AND** if found, proposes that location as the install target
- **AND** if not found, prompts the user for permission to create `.claude/` at the proposed path
- **AND** displays a summary of what will be installed (skills, agents, hook, specs/ scaffold)
- **AND** asks the user to confirm before proceeding (`Continue? [Y/n]`)
- **AND** creates `specs/reference/` and `specs/changes/` if missing
- **AND** exits 0 on success

#### Scenario: User cancels
- **WHEN** the user runs `spexl init claude` and responds "n" to the confirmation prompt
- **THEN** the system prints "Cancelled" and exits 0

#### Scenario: Init in a project with existing skills
- **GIVEN** the install target has been resolved
- **WHEN** spexl-generated skills already exist at the target location
- **THEN** the system prints a warning that skills already exist
- **AND** suggests `spexl update` instead
- **AND** exits 1

#### Scenario: Init unsupported target
- **WHEN** the user runs `spexl init <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

### Requirement: SessionStart hook installation
The system SHALL install a SessionStart hook in `.claude/settings.local.json` that runs `spexl prime` on session start.

#### Scenario: Hook installed during init
- **WHEN** `spexl init claude` completes successfully
- **THEN** `.claude/settings.local.json` contains a SessionStart hook that runs `spexl prime`
- **AND** if the file already exists, the hook is added without disturbing existing settings

#### Scenario: Hook already exists
- **WHEN** `spexl init claude` runs and a spexl SessionStart hook already exists in `.claude/settings.local.json`
- **THEN** the system skips hook installation and notes it in the summary

### Requirement: Update generated skills
The system SHALL support `spexl update` to regenerate skills, agents, and hook config. The target (e.g. claude) is detected from existing installation metadata.

#### Scenario: Update with no drift
- **WHEN** the user runs `spexl update` and generated files match what the current spexl version would produce
- **THEN** the system prints "Already up to date" and exits 0

#### Scenario: Update with template changes
- **WHEN** the user runs `spexl update` and the installed spexl version would produce different skills than what's on disk
- **THEN** the system regenerates each skill file
- **AND** prints a diff summary showing what changed per file
- **AND** overwrites existing skill files with regenerated content

#### Scenario: Update with no prior init
- **WHEN** the user runs `spexl update` but no spexl-generated skills exist
- **THEN** the system prints an error suggesting `spexl init claude`
- **AND** exits 1

### Requirement: Skill composition
The system SHALL compose each generated skill by assembling: (1) YAML frontmatter with name, description, and version, (2) action-specific instructions for the phase, (3) artifact templates inline where the skill frequently needs them, and (4) references to `spexl explain` for advanced topics and `spexl template` for less common artifact types.

#### Scenario: Generated propose skill
- **WHEN** `spexl init claude` generates the propose skill
- **THEN** the SKILL.md contains the propose-specific workflow
- **AND** contains the proposal template and spec-delta template inline
- **AND** does NOT contain foundational methodology (covered by `spexl prime` via hook)
- **AND** references `spexl explain spec-notation` for detailed notation guidance

#### Scenario: Generated skill is self-contained for its phase
- **WHEN** any generated skill is loaded by Claude Code
- **THEN** it contains all operational instructions needed to execute the phase
- **AND** does not require loading additional skills
- **AND** assumes foundational spexl knowledge is already in the system prompt via the SessionStart hook

<!-- UNCHANGED: Generation metadata, Agent generation -->
