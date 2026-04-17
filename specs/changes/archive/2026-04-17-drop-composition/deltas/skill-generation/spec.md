# Skill Generation

## MODIFIED Requirements

### Requirement: Init target
The system SHALL support `spexl init <target>` to install agent integration files into the current project. The initial supported target is `claude`. Init is idempotent: first run creates all files; subsequent runs refresh only files whose content has changed. The install walks the `spexl.content` package tree and copies files verbatim, preserving the directory layout.

#### Scenario: Init claude in a fresh project
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init claude`
- **THEN** the system creates `.claude/skills/learn-about-sdd-with-spexl/` with `SKILL.md` and a `references/` subdirectory containing one file per methodology reference (rules, concepts, spec-notation, structure, verification, critique, design-guidance, tasks-guidance, modes)
- **AND** creates `.claude/skills/spexl-<action>/SKILL.md` for each phase: explore, propose, refine, apply, archive
- **AND** creates `.claude/agents/spec-critic.md` and `.claude/agents/spec-sync.md`
- **AND** does NOT write `.claude/rules/spexl.md` (the onboard primer is for manual paste into AGENTS.md/CLAUDE.md)
- **AND** creates `.spexl.toml` with `[agents.claude]` and `install_path = ".claude/"`
- **AND** prints a summary of generated files

#### Scenario: Init claude when already installed
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl init claude`
- **THEN** the system compares each managed file's content against what would be installed
- **AND** overwrites only files whose content differs
- **AND** removes files under `.claude/skills/` and `.claude/agents/` that are no longer part of the content tree (stale files from previous installs)
- **AND** removes legacy `.claude/rules/spexl.md` if present
- **AND** prints a summary showing changed, unchanged, and removed counts

#### Scenario: Init with no target argument
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl init` without a target argument
- **THEN** the system refreshes all configured agent installations

#### Scenario: Init with no target and no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init` without a target argument
- **THEN** the system scaffolds a new project (creates `.spexl.toml` and `specs/` directory structure)

#### Scenario: Init unsupported target
- **WHEN** the user runs `spexl init <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Init --remove
- **GIVEN** `.spexl.toml` exists with a configured agent installation
- **WHEN** the user runs `spexl init --remove`
- **THEN** the system removes all spexl-managed files (skills, agents, legacy rules/spexl.md if present) at the configured install path
- **AND** removes `.spexl.toml`
- **AND** does NOT remove `specs/` or any user content
- **AND** prunes empty directories under the install path
- **AND** prints a summary of removed files

#### Scenario: Init --remove with no config
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init --remove`
- **THEN** the system prints "Nothing to remove" and exits 0

### Requirement: Agent generation
The system SHALL install agent definition files from `spexl.content.agents` into the target's agent directory. Agent frontmatter references the librarian skill by name so agents can load methodology knowledge from it.

#### Scenario: Install spec-critic agent for Claude
- **WHEN** `spexl init claude` runs
- **THEN** it copies `spexl.content.agents.spec-critic.md` to `.claude/agents/spec-critic.md`
- **AND** the installed file's frontmatter contains `skills: learn-about-sdd-with-spexl`

#### Scenario: Install spec-sync agent for Claude
- **WHEN** `spexl init claude` runs
- **THEN** it copies `spexl.content.agents.spec-sync.md` to `.claude/agents/spec-sync.md`
- **AND** the installed file's frontmatter contains `skills: learn-about-sdd-with-spexl`

## ADDED Requirements

### Requirement: Librarian skill
The system SHALL install a `learn-about-sdd-with-spexl` skill alongside the action skills. This skill holds the shared methodology content in a `references/` subdirectory. Action skills delegate methodology knowledge to this skill by instructing the agent to invoke it before proceeding.

#### Scenario: Librarian installed with references
- **WHEN** `spexl init claude` runs
- **THEN** `.claude/skills/learn-about-sdd-with-spexl/SKILL.md` is installed
- **AND** `.claude/skills/learn-about-sdd-with-spexl/references/` contains one markdown file per methodology topic (rules, concepts, spec-notation, structure, verification, critique, design-guidance, tasks-guidance, modes)

#### Scenario: Action skill references the librarian
- **WHEN** `spexl init claude` installs any action skill (`spexl-explore`, `spexl-propose`, `spexl-refine`, `spexl-apply`, `spexl-archive`)
- **THEN** the installed `SKILL.md` contains an instruction to invoke the `learn-about-sdd-with-spexl` skill before proceeding

## REMOVED Requirements

### Requirement: Skill composition
**Reason**: Skills are now hand-written at `src/spexl/content/skills/<name>/SKILL.md`. There is no composition engine, no partials, no manifest, and no assembly step. `src/spexl/generate/compose.py` has been deleted.

**Migration**: Contributors who previously edited partials (`templates/partials/*.md`) or action reference files (`templates/actions/*.md`) now edit the corresponding SKILL.md directly, or edit a reference file under the librarian skill. The `SKILL_MANIFESTS` dict is gone; there is no "add a partial to this skill" operation.

### Requirement: Generation metadata
**Reason**: Skills are installed verbatim from source. There is no generation step to record. The `metadata:` frontmatter block (with `generated_by` and `generated_on`) is no longer written.

**Migration**: Tools that parsed `generated_by` or `generated_on` from installed SKILL.md files must be updated to read the spexl version from another source (e.g., `spexl --version`) or drop the dependency. The version of the content matches the installed spexl package version.
