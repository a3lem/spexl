# CLI

## MODIFIED Requirements

### Requirement: CLI entry point
The system SHALL expose a `spexl` command via `[project.scripts]` in pyproject.toml, routing to subcommand handlers in `src/spexl/cli/`.

#### Scenario: Invoke with no arguments
- **WHEN** the user runs `spexl` with no arguments
- **THEN** the system prints a usage summary listing all available subcommands
- **AND** exits 0

#### Scenario: Invoke with unknown subcommand
- **WHEN** the user runs `spexl <unknown>`
- **THEN** the system prints an error with the unknown command name and a suggestion to run `spexl --help`
- **AND** exits 1

#### Scenario: Invoke existing plumbing command
- **WHEN** the user runs `spexl new <slug>`, `spexl changes`, `spexl validate`, `spexl info`, `spexl refs`, `spexl link`, or `spexl unlink`
- **THEN** the system routes to the appropriate command handler

#### Scenario: Invoke init or install
- **WHEN** the user runs `spexl init` or `spexl install [<target>]`
- **THEN** the system routes to the scaffold handler or the agent-install handler respectively

#### Scenario: Invoke removed subcommand
- **WHEN** the user runs `spexl archived`
- **THEN** the system prints an error with the unknown command name
- **AND** exits 1

### Requirement: Init scaffolds project
The system SHALL support `spexl init` (no arguments) to scaffold a spexl project in the current directory: it creates `.spexl.toml` and `specs/changes/` / `specs/reference/` directories. `spexl init` performs no agent-asset installation; agent setup lives under `spexl install`. When the directory is already fully initialized (both `.spexl.toml` and the configured specs directory exist), init exits 0 and prints a short notice to stderr without modifying anything. Partial states (missing config or missing specs directory) are backfilled.

#### Scenario: Init in empty directory
- **WHEN** the user runs `spexl init` in a directory with no `.spexl.toml`
- **THEN** the system creates `.spexl.toml` with default `[specs_location]` and `specs/changes/` and `specs/reference/` directories
- **AND** prints the created paths

#### Scenario: Init in subdir with parent project
- **GIVEN** a parent directory containing `.spexl.toml`
- **WHEN** the user runs `spexl init` in a subdirectory with no `.spexl.toml`
- **THEN** the system creates `.spexl.toml` and `specs/` structure in the current directory
- **AND** walks UP to detect the parent project (see project-config walk-up boundary)
- **AND** prints a note indicating a parent project was found

#### Scenario: Init in already-initialized directory
- **GIVEN** a directory with `.spexl.toml` and the configured specs directory already present
- **WHEN** the user runs `spexl init`
- **THEN** the system prints `spexl already initialized in this directory` to stderr
- **AND** does not modify `.spexl.toml` or any file under the specs directory
- **AND** exits 0

#### Scenario: Init backfills missing specs directories
- **GIVEN** a directory with `.spexl.toml` but no specs directory
- **WHEN** the user runs `spexl init`
- **THEN** the system creates `specs/changes/` and `specs/reference/`
- **AND** does not modify the existing `.spexl.toml`
- **AND** exits 0

#### Scenario: Init does not overwrite specs
- **GIVEN** a directory with no `.spexl.toml` but an existing `specs/` directory
- **WHEN** the user runs `spexl init`
- **THEN** the system creates `.spexl.toml`
- **AND** creates only missing subdirectories under `specs/`
- **AND** does not modify existing files

#### Scenario: Init rejects target argument
- **WHEN** the user runs `spexl init <anything>`
- **THEN** the system prints an error indicating `init` takes no arguments and suggests `spexl install <target>` for agent setup
- **AND** exits 1

### Requirement: Package structure
The system SHALL be structured as a Python package under `src/spexl/` with the following layout:

```
src/spexl/
├── __init__.py          # main() entry point, top-level argparse
├── errors.py            # SpexlError
├── specroot.py          # Spec root discovery, change resolution, .change.json I/O
├── config.py            # .spexl.toml parsing and defaults
├── cli/
│   ├── changes.py       # new, changes, info, archive
│   ├── links.py         # link, unlink
│   ├── validate.py      # validate (+ --fix)
│   ├── refs.py          # refs
│   ├── install.py       # init (scaffold), install (agent assets)
│   └── steering.py      # onboard
└── content/             # Package data: skills, agents, onboard primer
    ├── skills/
    │   ├── spexl-how-to-use/               # methodology skill with references/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   │       ├── rules.md
    │   │       ├── concepts.md
    │   │       ├── spec-notation.md
    │   │       ├── structure.md
    │   │       ├── verification.md
    │   │       ├── critique.md
    │   │       ├── design-guidance.md
    │   │       ├── tasks-guidance.md
    │   │       └── modes.md
    │   └── spexl-<action>/SKILL.md         # one per phase: explore, propose, refine, apply, archive
    ├── agents/
    │   ├── spexl-spec-critic.md
    │   └── spexl-spec-sync.md
    └── onboard.md
```

The global `--cwd` option sets the starting directory for `.spexl.toml` discovery. Default: current working directory.

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** content files are accessible via `importlib.resources` from the `spexl.content` package

#### Scenario: Explicit project directory
- **WHEN** the user runs `spexl --cwd /path/to/project changes`
- **THEN** the system starts `.spexl.toml` discovery from `/path/to/project/`

#### Scenario: Default project directory
- **WHEN** the user runs `spexl changes` without `--cwd`
- **THEN** the system starts `.spexl.toml` discovery from the current working directory

### Requirement: Subcommand routing
The system SHALL use argparse with subparsers to route to command handlers. Each CLI module (`changes`, `links`, `validate`, `refs`, `install`, `steering`) exposes a `register(subparsers)` function called by `main()`. The `install` module registers both the `init` and `install` subparsers.

#### Scenario: Help for a specific subcommand
- **WHEN** the user runs `spexl <subcommand> --help`
- **THEN** the system prints subcommand-specific usage and exits 0

## ADDED Requirements

### Requirement: Install command
The system SHALL support `spexl install [<target>]` to install, refresh, or remove spexl agent integration files. The installation behavior lives in the `skill-generation` capability; this requirement defines the CLI surface that routes to it.

#### Scenario: Install with target
- **WHEN** the user runs `spexl install <target>` (e.g. `spexl install claude`)
- **THEN** the system routes to the agent-install handler for that target

#### Scenario: Install without target
- **WHEN** the user runs `spexl install` with no target
- **THEN** the system routes to the refresh handler, which refreshes every configured agent installation

#### Scenario: Install with unknown target
- **WHEN** the user runs `spexl install <unknown-target>`
- **THEN** the system prints an error listing supported targets
- **AND** exits 1

#### Scenario: Install --remove
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system routes to the remove handler, which deletes managed agent files and clears `[agents]` from `.spexl.toml`

#### Scenario: Install help
- **WHEN** the user runs `spexl install --help`
- **THEN** the system prints usage for the install command, listing supported targets and the `--remove` flag
