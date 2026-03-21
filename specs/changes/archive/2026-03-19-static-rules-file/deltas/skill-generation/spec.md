## MODIFIED Requirements

### Requirement: Init target
The system SHALL support `spexl init <target>` to generate agent integration files into the current project. The initial supported target is `claude`.

#### Scenario: Init claude in a fresh project
- **WHEN** the user runs `spexl init claude` in a project with no existing `.claude/skills/` directory
- **THEN** the system creates `.claude/skills/` with one SKILL.md per action (propose, apply, explore, refine, archive)
- **AND** creates `.claude/agents/` with agent definitions (spec-critic, spec-sync)
- **AND** writes `.claude/rules/spexl.md` containing the output of `spexl prime`
- **AND** creates `specs/` directory structure if missing (`specs/reference/`, `specs/changes/`)
- **AND** prints a summary of generated files

#### Scenario: Init claude in a project with existing skills
- **WHEN** the user runs `spexl init claude` and `.claude/skills/` already contains spexl-generated skills
- **THEN** the system prints a warning that skills already exist
- **AND** suggests `spexl update` instead
- **AND** exits 1

#### Scenario: Init unsupported target
- **WHEN** the user runs `spexl init <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

### Requirement: Update generated skills
The system SHALL support `spexl update` to regenerate agent integration files and the rules file when the spexl version changes.

#### Scenario: Update with no drift
- **WHEN** the user runs `spexl update` and generated files match what the current spexl version would produce
- **THEN** the system prints "Already up to date" and exits 0

#### Scenario: Update with template changes
- **WHEN** the user runs `spexl update` and the installed spexl version would produce different output than what's on disk
- **THEN** the system regenerates each skill file and `.claude/rules/spexl.md`
- **AND** prints a diff summary showing what changed per file
- **AND** overwrites existing files with regenerated content

#### Scenario: Update with no prior init
- **WHEN** the user runs `spexl update` but no spexl-generated skills exist
- **THEN** the system prints an error suggesting `spexl init claude`
- **AND** exits 1

### Requirement: Skill composition
The system SHALL compose each generated skill by assembling: (1) YAML frontmatter with name, description, and version, (2) shared partials (rules, directory structure, cross-phase context), (3) action-specific instructions, and (4) references to spexl CLI commands for runtime steering and plumbing. Skills SHALL NOT include foundational methodology content, which is covered by the rules file.

#### Scenario: Generated propose skill
- **WHEN** `spexl init claude` generates the propose skill
- **THEN** the SKILL.md contains the shared rules from `templates/partials/`
- **AND** contains the propose-specific workflow from `templates/actions/propose.md`
- **AND** references `spexl explain` for advanced context
- **AND** references `spexl template` for artifact templates
- **AND** references `spexl new <slug>` for directory scaffolding
- **AND** does NOT contain foundational methodology (covered by `.claude/rules/spexl.md`)

#### Scenario: Generated skill is self-contained
- **WHEN** any generated skill is loaded by Claude Code
- **THEN** it contains all rules and instructions needed to execute the action
- **AND** does not reference other SKILL.md files or require loading additional skills
- **AND** calls `spexl` CLI commands for plumbing and on-demand context only
- **AND** assumes foundational spexl knowledge is already in the system prompt via the rules file

<!-- UNCHANGED: Generation metadata, Agent generation -->
