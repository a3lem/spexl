# Skill Generation

## MODIFIED Requirements

### Requirement: Install target
The system SHALL support `spexl install <target>` to install agent integration files into the current project. The initial supported target is `claude`. Install is idempotent: first run creates all files; subsequent runs refresh only files whose content has changed. The install walks the `spexl.content` package tree and copies files verbatim, preserving the directory layout. `install` writes or updates `.spexl.toml` only to record the `[agents.<target>]` section; creating the `specs/` directory structure is the separate responsibility of `spexl init`.

#### Scenario: Install claude in a fresh project
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl install claude`
- **THEN** the system creates `.claude/skills/spexl-foundations/` with `SKILL.md` and a `references/` subdirectory containing one file per methodology reference (rules, concepts, spec-notation, structure, verification, critique, design-guidance, tasks-guidance, modes)
- **AND** creates `.claude/skills/spexl-<action>/SKILL.md` for each phase: explore, propose, refine, apply, archive
- **AND** creates `.claude/agents/spexl-spec-critic.md` and `.claude/agents/spexl-spec-sync.md`
- **AND** does NOT write `.claude/rules/spexl.md` (the onboard primer is for manual paste into AGENTS.md/CLAUDE.md)
- **AND** creates `.spexl.toml` with `[agents.claude]` and `install_path = ".claude/"`
- **AND** does NOT create `specs/` directories (that is `spexl init`'s job)
- **AND** prints a summary of generated files

#### Scenario: Install claude when already installed
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl install claude`
- **THEN** the system compares each managed file's content against what would be installed
- **AND** overwrites only files whose content differs
- **AND** removes files under `.claude/skills/` and `.claude/agents/` that are no longer part of the content tree (stale files from previous installs)
- **AND** removes legacy `.claude/rules/spexl.md` if present
- **AND** prints a summary showing changed, unchanged, and removed counts

#### Scenario: Install with no target argument
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl install` without a target argument
- **THEN** the system refreshes all configured agent installations

#### Scenario: Install with no target and no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl install` without a target argument
- **THEN** the system prints an error indicating no config was found and suggests `spexl init` (to scaffold a project) followed by `spexl install <target>`
- **AND** exits 1

#### Scenario: Install with no target and no agents configured
- **GIVEN** `.spexl.toml` exists with no `[agents]` section
- **WHEN** the user runs `spexl install` without a target argument
- **THEN** the system prints an error suggesting `spexl install <target>`
- **AND** exits 1

#### Scenario: Install unsupported target
- **WHEN** the user runs `spexl install <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Install --remove
- **GIVEN** `.spexl.toml` exists with a configured agent installation
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system removes all spexl-managed files (skills, agents, legacy rules/spexl.md if present) at the configured install path
- **AND** removes the `[agents]` section from `.spexl.toml` (without deleting the file)
- **AND** does NOT remove `specs/` or any user content
- **AND** prunes empty directories under the install path
- **AND** prints a summary of removed files

#### Scenario: Install --remove with no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system prints "Nothing to remove" and exits 0

### Requirement: Methodology skill
The system SHALL install a `spexl-foundations` skill alongside the action skills. This skill holds the shared methodology content in a `references/` subdirectory. Action skills delegate methodology knowledge to this skill by instructing the agent to invoke it before proceeding.

#### Scenario: Methodology skill installed with references
- **WHEN** `spexl install claude` runs
- **THEN** `.claude/skills/spexl-foundations/SKILL.md` is installed
- **AND** `.claude/skills/spexl-foundations/references/` contains one markdown file per methodology topic (rules, concepts, spec-notation, structure, verification, critique, design-guidance, tasks-guidance, modes)

#### Scenario: Action skill references the methodology skill
- **WHEN** `spexl install claude` installs any action skill (`spexl-explore`, `spexl-propose`, `spexl-refine`, `spexl-apply`, `spexl-archive`)
- **THEN** the installed `SKILL.md` contains an instruction to invoke the `spexl-foundations` skill before proceeding
- **AND** the installed `SKILL.md` does NOT reference any file path inside `spexl-foundations/` (action skills defer routing to the methodology skill instead of naming its internal files)

### Requirement: Agent generation
The system SHALL install agent definition files from `spexl.content.agents` into the target's agent directory. Agent frontmatter references the methodology skill by name so agents can load methodology knowledge from it.

#### Scenario: Install spexl-spec-critic agent for Claude
- **WHEN** `spexl install claude` runs
- **THEN** it copies `spexl.content.agents.spexl-spec-critic.md` to `.claude/agents/spexl-spec-critic.md`
- **AND** the installed file's frontmatter contains `skills: spexl-foundations`

#### Scenario: Install spexl-spec-sync agent for Claude
- **WHEN** `spexl install claude` runs
- **THEN** it copies `spexl.content.agents.spexl-spec-sync.md` to `.claude/agents/spexl-spec-sync.md`
- **AND** the installed file's frontmatter contains `skills: spexl-foundations`
