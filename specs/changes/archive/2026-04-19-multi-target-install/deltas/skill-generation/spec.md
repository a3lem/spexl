# Skill Generation

## MODIFIED Requirements

### Requirement: Install target
The system SHALL support `spexl install --target <target>` (short form: `-t`) to install agent integration files into the current project. Supported targets are members of the `Target` enum: `claude`, `opencode`, `pi`. The `--target` flag is mandatory on first install. Without `--target`, the system refreshes all targets listed in `.spexl.toml`. Install is idempotent: first run creates all files; subsequent runs refresh only files whose content has changed. Install renders Jinja2 templates from the `spexl.content.templates` package with per-target context, writing the output to target-specific destination paths. `install` writes or updates `.spexl.toml` only to record the `[agents.<target>]` section; creating the `specs/` directory structure is the separate responsibility of `spexl init`.

#### Scenario: Install claude
- **GIVEN** no `.spexl.toml` exists
- **WHEN** the user runs `spexl install -t claude`
- **THEN** the system renders templates with target=claude context
- **AND** writes skills to `.claude/skills/spexl-*/`
- **AND** writes agents to `.claude/agents/`
- **AND** writes a rules file to `.claude/rules/sdd-with-spexl.md` containing the methodology primer
- **AND** merges hook definitions into `.claude/settings.json`
- **AND** creates `.spexl.toml` with `[agents.claude]`
- **AND** prints a summary of generated files

#### Scenario: Install opencode
- **GIVEN** no `.spexl.toml` exists
- **WHEN** the user runs `spexl install -t opencode`
- **THEN** the system renders templates with target=opencode context
- **AND** writes skills to `.agents/skills/spexl-*/`
- **AND** writes a rules file to `.agents/rules/sdd-with-spexl.md`
- **AND** drops hook packages to `.opencode/plugins/`
- **AND** creates `.spexl.toml` with `[agents.opencode]`

#### Scenario: Install pi
- **GIVEN** no `.spexl.toml` exists
- **WHEN** the user runs `spexl install -t pi`
- **THEN** the system renders templates with target=pi context
- **AND** writes skills to `.agents/skills/spexl-*/`
- **AND** writes a rules file to `.agents/rules/sdd-with-spexl.md`
- **AND** drops extension modules to `.pi/extensions/`
- **AND** creates `.spexl.toml` with `[agents.pi]`

#### Scenario: Install when already installed (refresh)
- **GIVEN** `.spexl.toml` exists with `[agents.claude]`
- **WHEN** the user runs `spexl install -t claude`
- **THEN** the system compares each managed file's content against what would be rendered
- **AND** overwrites only files whose content differs
- **AND** removes files under managed directories that are no longer part of the template tree
- **AND** prints a summary showing changed, unchanged, and removed counts

#### Scenario: Install without target refreshes all
- **GIVEN** `.spexl.toml` exists with `[agents.claude]` and `[agents.opencode]`
- **WHEN** the user runs `spexl install` without `--target`
- **THEN** the system refreshes both claude and opencode installations

#### Scenario: Install with no target and no config
- **GIVEN** no `.spexl.toml` exists
- **WHEN** the user runs `spexl install` without `--target`
- **THEN** the system prints an error suggesting `spexl init` then `spexl install -t <target>`
- **AND** exits 1

#### Scenario: Install with no target and no agents configured
- **GIVEN** `.spexl.toml` exists with no `[agents]` section
- **WHEN** the user runs `spexl install` without `--target`
- **THEN** the system prints an error suggesting `spexl install -t <target>`
- **AND** exits 1

#### Scenario: Install unsupported target
- **WHEN** the user runs `spexl install -t unknown`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Install --remove
- **GIVEN** `.spexl.toml` exists with configured agent installations
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system removes all spexl-managed files for every configured target
- **AND** for claude, removes hook definitions from `.claude/settings.json` (identified by managed-by marker)
- **AND** removes the `[agents]` section from `.spexl.toml` but does NOT delete `.spexl.toml` itself
- **AND** does NOT remove `specs/` or any other project content
- **AND** prunes empty directories under managed paths only
- **AND** prints a summary of removed files

#### Scenario: Install --remove with no config
- **GIVEN** no `.spexl.toml` exists
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system prints "Nothing to remove" and exits 0

## ADDED Requirements

### Requirement: Template rendering
The system SHALL render Jinja2 templates from the `spexl.content.templates` package with a per-target context dict. The context includes at minimum `target` (the target name) and `managed_marker` (the comment text identifying the file as spexl-managed). Templates produce the final content of skills, rules, agents, and hook definitions. Template errors are fatal and report the template path and Jinja2 error message.

#### Scenario: Template with target-specific content
- **GIVEN** a skill template containing `{% if target == "claude" %}use AskUserQuestion{% else %}ask the user directly{% endif %}`
- **WHEN** rendered with target=claude
- **THEN** the output contains "use AskUserQuestion"

#### Scenario: Template with target=opencode
- **GIVEN** the same template as above
- **WHEN** rendered with target=opencode
- **THEN** the output contains "ask the user directly"

#### Scenario: Template rendering error
- **GIVEN** a template with a Jinja2 syntax error
- **WHEN** the install command attempts to render it
- **THEN** the system prints the template path and Jinja2 error
- **AND** exits 1

### Requirement: Managed-file marker
The system SHALL include a managed-file marker comment in every generated file. The marker identifies the file as generated by spexl and warns against manual editing. The marker format adapts to the file type: `<!-- managed by spexl -->` for Markdown, `// managed by spexl` for JSON/JS, `# managed by spexl` for TOML/YAML. The `--remove` command uses these markers (and the `.spexl.toml` manifest) to identify files to clean up.

#### Scenario: Markdown file marker
- **WHEN** install generates a `.md` file
- **THEN** the first line of the file is `<!-- managed by spexl - do not edit -->`

#### Scenario: JSON hook marker
- **WHEN** install merges a hook definition into `.claude/settings.json`
- **THEN** the hook definition includes a `"_managed_by": "spexl"` field

#### Scenario: JS/TS extension marker
- **WHEN** install generates a `.js` or `.ts` file for opencode or pi
- **THEN** the first line is `// managed by spexl - do not edit`

### Requirement: Per-target destination mapping
The system SHALL map artifact types to target-specific destination paths. Each target defines where skills, rules, hooks, and agents are written.

#### Scenario: Claude destination paths
- **WHEN** installing for target=claude
- **THEN** skills go to `.claude/skills/`
- **AND** agents go to `.claude/agents/`
- **AND** rules go to `.claude/rules/`
- **AND** hooks are merged into `.claude/settings.json`

#### Scenario: opencode destination paths
- **WHEN** installing for target=opencode
- **THEN** skills go to `.agents/skills/`
- **AND** rules go to `.agents/rules/`
- **AND** hooks go to `.opencode/plugins/`

#### Scenario: pi destination paths
- **WHEN** installing for target=pi
- **THEN** skills go to `.agents/skills/`
- **AND** rules go to `.agents/rules/`
- **AND** hooks go to `.pi/extensions/`

### Requirement: Claude hook installation
The system SHALL install hooks for Claude Code by reading `.claude/settings.json`, merging spexl hook definitions into the `hooks` object, and writing the file back. Each spexl-managed hook includes a `"_managed_by": "spexl"` field. The merge preserves all non-spexl entries. If `.claude/settings.json` does not exist, install creates it. If the file contains invalid JSON, install prints an error and exits 1 without modifying the file.

#### Scenario: Merge hooks into existing settings
- **GIVEN** `.claude/settings.json` contains user-defined hooks
- **WHEN** install writes spexl hooks
- **THEN** the user's hooks are preserved
- **AND** spexl hooks are added with `_managed_by` markers

#### Scenario: Create settings.json
- **GIVEN** `.claude/settings.json` does not exist
- **WHEN** install writes spexl hooks
- **THEN** `.claude/settings.json` is created with only the spexl hooks

#### Scenario: Invalid settings.json
- **GIVEN** `.claude/settings.json` contains invalid JSON
- **WHEN** install attempts to merge hooks
- **THEN** the system prints an error identifying the file and parse error
- **AND** exits 1 without modifying the file

#### Scenario: Remove spexl hooks
- **WHEN** `spexl install --remove` runs for a claude target
- **THEN** entries with `"_managed_by": "spexl"` are removed from `.claude/settings.json`
- **AND** all other entries in settings.json are preserved

### Requirement: Rules file generation
The system SHALL generate a rules file containing the spexl methodology primer (formerly served by the `onboard` command). The rules file is rendered from a template and installed to the target's rules directory. This replaces the manual `spexl onboard >> AGENTS.md` workflow.

#### Scenario: Rules file content
- **WHEN** install generates the rules file
- **THEN** the file contains the five-phase workflow summary, core rules, directory layout, and a pointer to the spexl-foundations skill
- **AND** the file begins with a managed-file marker

### Requirement: Methodology skill
The system SHALL install a `spexl-foundations` skill alongside the action skills. This skill holds the shared methodology content in a `references/` subdirectory. Action skills delegate methodology knowledge to this skill by instructing the agent to invoke it before proceeding.

#### Scenario: Methodology skill installed with references
- **WHEN** `spexl install -t claude` runs
- **THEN** `.claude/skills/spexl-foundations/SKILL.md` is installed
- **AND** `.claude/skills/spexl-foundations/references/` contains one markdown file per methodology topic

#### Scenario: Action skill references the methodology skill
- **WHEN** `spexl install -t claude` installs any action skill
- **THEN** the installed `SKILL.md` contains an instruction to invoke the `spexl-foundations` skill before proceeding

### Requirement: Agent generation
The system SHALL install agent definition files from templates into the target's agent directory. Agent frontmatter references the methodology skill by name.

#### Scenario: Install agents for Claude
- **WHEN** `spexl install -t claude` runs
- **THEN** `.claude/agents/spexl-spec-critic.md` and `.claude/agents/spexl-spec-sync.md` are installed

#### Scenario: Agents for targets without agent support
- **GIVEN** a target that does not support agent definitions
- **WHEN** install runs for that target
- **THEN** no agent files are generated
