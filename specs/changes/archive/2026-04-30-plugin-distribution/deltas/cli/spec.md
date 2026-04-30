# CLI

## MODIFIED Requirements

### Requirement: Package structure
The system SHALL be structured as a Python package under `src/spexl/` with the following layout:

```
src/spexl/
├── __init__.py          # main() entry point, top-level argparse
├── errors.py            # SpexlError
├── specroot.py          # Spec root discovery, change resolution, .change.json I/O
├── config.py            # .spexl.toml parsing and defaults
└── cli/
    ├── changes.py       # new, changes, info, archive
    ├── links.py         # link, unlink
    ├── validate.py      # validate (+ --fix)
    ├── refs.py          # refs
    └── install.py       # init (scaffold only)
```

The `content/` package is removed. Skills, agents, and rules live at the repository root and are distributed via native plugins, not the Python package. The global `--cwd` option sets the starting directory for `.spexl.toml` discovery. Default: current working directory.

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** the package does NOT include skills, agents, or rules content

#### Scenario: Explicit project directory
- **WHEN** the user runs `spexl --cwd /path/to/project changes`
- **THEN** the system starts `.spexl.toml` discovery from `/path/to/project/`

#### Scenario: Default project directory
- **WHEN** the user runs `spexl changes` without `--cwd`
- **THEN** the system starts `.spexl.toml` discovery from the current working directory

### Requirement: Subcommand routing
The system SHALL use argparse with subparsers to route to command handlers. Each CLI module (`changes`, `links`, `validate`, `refs`, `install`) exposes a `register(subparsers)` function called by `main()`. The `install` module registers only the `init` subparser.

#### Scenario: Help for a specific subcommand
- **WHEN** the user runs `spexl <subcommand> --help`
- **THEN** the system prints subcommand-specific usage and exits 0

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

#### Scenario: Invoke init
- **WHEN** the user runs `spexl init`
- **THEN** the system routes to the scaffold handler

#### Scenario: Invoke removed subcommand (install)
- **WHEN** the user runs `spexl install`
- **THEN** the system prints an error explaining that `install` has been removed and content is now distributed via native plugins
- **AND** exits 1

#### Scenario: Invoke removed subcommand (onboard)
- **WHEN** the user runs `spexl onboard`
- **THEN** the system prints an error explaining that `onboard` has been removed and the methodology primer is now delivered via `AGENTS.md`/`CLAUDE.md` in the plugin
- **AND** exits 1

## REMOVED Requirements

### Requirement: Install command
**Reason**: The `install` command managed per-target content generation and file routing. This responsibility moves to each coding agent's native plugin system. The CLI retains only `init` for project scaffolding.
**Migration**: Users install the spexl plugin via their agent's native mechanism instead of running `spexl install <target>`.

### Requirement: Init rejects target argument
**Reason**: With `install` removed, there is no `spexl install <target>` to redirect to. The helpful error for `spexl init <target>` is no longer needed.
**Migration**: Standard argparse error for unexpected arguments.
