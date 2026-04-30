# Skill Generation

## REMOVED Requirements

### Requirement: Install target
**Reason**: The `install` command and its per-target content generation are replaced by native plugin distribution. Each coding agent's plugin system handles file routing. No CLI-driven install, refresh, or remove is needed.
**Migration**: Users install the spexl plugin via their agent's native mechanism (e.g., `claude plugin install`, opencode.json reference, pi plugin install). The CLI retains `spexl init` for project scaffolding.

### Requirement: Methodology skill
**Reason**: The methodology skill (`spexl-foundations`) still exists but is no longer "installed" by the CLI. It lives at `skills/spexl-foundations/` in the repo root and is delivered by the plugin system.
**Migration**: Content is identical. Only the delivery mechanism changes.

### Requirement: Agent generation
**Reason**: Agent definition files are no longer copied by the CLI. They live at `agents/` in the repo root and are delivered by the plugin system.
**Migration**: Content is identical. Only the delivery mechanism changes.

## ADDED Requirements

### Requirement: Repo-root content layout
The system SHALL maintain skills, rules, and agent definitions at the repository root, outside `src/spexl/`. These files are consumed directly by coding agent plugins and are NOT bundled into the Python package.

#### Scenario: Skills at repo root
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects the root directory
- **THEN** `skills/` contains `spexl-foundations/` (with `SKILL.md` and `references/` subdirectory) and one directory per action skill (`spexl-explore/`, `spexl-propose/`, `spexl-refine/`, `spexl-apply/`, `spexl-archive/`), each containing `SKILL.md`

#### Scenario: Agents at repo root
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects the root directory
- **THEN** `agents/` contains `spexl-spec-critic.md` and `spexl-spec-sync.md`

#### Scenario: Methodology primer as AGENTS.md
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects the root directory
- **THEN** `AGENTS.md` contains the methodology primer (workflow phases, core rules, directory layout, pointer to spexl-foundations skill)
- **AND** `CLAUDE.md` at plugin root contains Claude-specific context and tool-mapping notes

#### Scenario: Standard content directories
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects the root directory
- **THEN** `commands/` and `hooks/` directories exist (following superpowers convention, empty for now)

#### Scenario: Content not in Python package
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the installed package does NOT include skills, agents, or rules files
- **AND** `importlib.resources.files("spexl.content")` is no longer available

### Requirement: Per-agent plugin manifests
The repository SHALL contain plugin manifests for each supported coding agent at the repo root. Each agent's plugin system auto-discovers shared content (`skills/`, `agents/`, `commands/`, `hooks/`) from the repo root. Context files (`AGENTS.md`, `CLAUDE.md`) are loaded per each agent's convention.

#### Scenario: Claude Code plugin manifest
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects `.claude-plugin/`
- **THEN** it contains a `plugin.json` with name, description, version, author, and standard metadata
- **AND** does NOT declare explicit paths (Claude Code auto-discovers by convention)

#### Scenario: opencode plugin config
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects `.opencode/`
- **THEN** it contains configuration that exposes the shared skills and rules to opencode

#### Scenario: pi plugin config
- **GIVEN** a cloned spexl repository
- **WHEN** a user inspects `.pi/`
- **THEN** it contains configuration that exposes the shared skills and rules to pi
- **AND** does NOT reference agent definitions (pi does not support subagents)

### Requirement: Per-agent context via AGENTS.md and CLAUDE.md
The repository SHALL provide agent-specific context through convention files at the plugin root. `AGENTS.md` provides methodology context for agents that load it (opencode, pi). `CLAUDE.md` provides Claude-specific context including tool-mapping notes. These replace the old `onboard` command and any per-agent `rules/` directories.

#### Scenario: Claude loads plugin CLAUDE.md
- **GIVEN** the Claude Code plugin is installed
- **WHEN** the agent loads plugin context
- **THEN** the plugin's `CLAUDE.md` is loaded, providing methodology primer and Claude-specific tool-mapping notes

#### Scenario: opencode/pi loads AGENTS.md
- **GIVEN** the opencode or pi plugin is installed
- **WHEN** the agent loads plugin context
- **THEN** `AGENTS.md` is loaded, providing the methodology primer
