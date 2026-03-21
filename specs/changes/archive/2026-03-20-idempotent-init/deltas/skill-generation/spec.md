## MODIFIED Requirements

### Requirement: Init target
The system SHALL support `spexl init <target>` to generate agent integration files into the current project. The initial supported target is `claude`. Init is idempotent: first run creates all files, subsequent runs refresh only files whose content has changed.

#### Scenario: Init claude in a fresh project
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init claude`
- **THEN** the system creates `.claude/skills/` with one SKILL.md per action (propose, apply, explore, refine, archive)
- **AND** creates `.claude/agents/` with agent definitions (spec-critic, spec-sync)
- **AND** writes `.claude/rules/spexl.md` containing the output of `spexl prime`
- **AND** creates `.spexl.toml` with `[agents.claude]` and `install_path = ".claude"`
- **AND** prints a summary of generated files

#### Scenario: Init claude when already installed
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl init claude`
- **THEN** the system compares each managed file's content against what would be generated
- **AND** overwrites only files whose content differs
- **AND** prints a summary showing what changed (e.g. "3 files changed, 5 unchanged")

#### Scenario: Init with no target argument
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl init` without a target argument
- **THEN** the system refreshes all configured agent installations

#### Scenario: Init with no target and no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init` without a target argument
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Init unsupported target
- **WHEN** the user runs `spexl init <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Init --remove
- **GIVEN** `.spexl.toml` exists with a configured agent installation
- **WHEN** the user runs `spexl init --remove`
- **THEN** the system removes all spexl-managed files (skills, agents, rules file) at the configured install path
- **AND** removes `.spexl.toml`
- **AND** does NOT remove `specs/` or any user content
- **AND** prints a summary of removed files

#### Scenario: Init --remove with no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init --remove`
- **THEN** the system prints "Nothing to remove" and exits 0

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

### Requirement: Generation metadata
The system SHALL embed metadata in each generated file's YAML frontmatter indicating the spexl version that produced it and a timestamp.

#### Scenario: Metadata in generated SKILL.md frontmatter
- **Given** spexl version is 0.2.0
- **WHEN** a skill is generated
- **THEN** the YAML frontmatter contains a `metadata` block with `generated_by: spexl 0.2.0` and `generated_on: YYYY-MM-DD`

### Requirement: Agent generation
The system SHALL generate agent definition files from `templates/agents/` into the target's agent directory.

#### Scenario: Generate spec-critic agent for Claude
- **WHEN** `spexl init claude` runs
- **THEN** it copies `templates/agents/spec-critic.md` to `.claude/agents/spec-critic.md`

#### Scenario: Generate spec-sync agent for Claude
- **WHEN** `spexl init claude` runs
- **THEN** it copies `templates/agents/spec-sync.md` to `.claude/agents/spec-sync.md`

## REMOVED Requirements

### Requirement: Update generated skills
**Reason**: `spexl update` is removed. Its functionality is absorbed into `spexl init`, which is now idempotent.
**Migration**: Use `spexl init` (no target arg) to refresh installed files.
