# CLI

## MODIFIED Requirements

### Requirement: Install command
The system SHALL support `spexl install` to install, refresh, or remove spexl agent integration files. The `--target`/`-t` flag specifies the target agent. The `--remove` flag removes all managed files.

#### Scenario: Install with target flag
- **WHEN** the user runs `spexl install -t claude`
- **THEN** the system routes to the agent-install handler for claude

#### Scenario: Install with long flag
- **WHEN** the user runs `spexl install --target opencode`
- **THEN** the system routes to the agent-install handler for opencode

#### Scenario: Install without target
- **GIVEN** `.spexl.toml` exists with configured agents
- **WHEN** the user runs `spexl install` with no `--target` flag
- **THEN** the system routes to the refresh handler for all configured targets

#### Scenario: Install with unknown target
- **WHEN** the user runs `spexl install -t unknown`
- **THEN** the system prints an error listing supported targets (claude, opencode, pi)
- **AND** exits 1

#### Scenario: Install --remove
- **WHEN** the user runs `spexl install --remove`
- **THEN** the system routes to the remove handler

#### Scenario: Install help
- **WHEN** the user runs `spexl install --help`
- **THEN** the system prints usage listing `--target`/`-t`, supported targets, and `--remove`

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
│   └── install.py       # init (scaffold), install (agent assets)
└── content/             # Package data: templates, hooks, static references
    └── templates/       # Jinja2 templates for skills, agents, rules, hooks
```

The global `--cwd` option sets the starting directory for `.spexl.toml` discovery. Default: current working directory.

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** templates are accessible via `importlib.resources` from the `spexl.content.templates` package

#### Scenario: Explicit project directory
- **WHEN** the user runs `spexl --cwd /path/to/project install -t claude`
- **THEN** the system starts `.spexl.toml` discovery from `/path/to/project/`

#### Scenario: Default project directory
- **WHEN** the user runs `spexl install -t claude` without `--cwd`
- **THEN** the system starts `.spexl.toml` discovery from the current working directory

### Requirement: Subcommand routing
The system SHALL use argparse with subparsers to route to command handlers. Each CLI module (`changes`, `links`, `validate`, `refs`, `install`) exposes a `register(subparsers)` function called by `main()`. The `install` module registers both the `init` and `install` subparsers.

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

#### Scenario: Invoke init or install
- **WHEN** the user runs `spexl init` or `spexl install [-t <target>]`
- **THEN** the system routes to the scaffold handler or the agent-install handler respectively

#### Scenario: Invoke removed subcommand
- **WHEN** the user runs `spexl onboard`
- **THEN** the system prints an error suggesting `spexl install -t <target>` as the replacement
- **AND** exits 1

## REMOVED Requirements

### Requirement: Init rejects target argument
**Reason**: The `spexl init <target>` redirect is no longer needed. `install` now uses `--target`/`-t`, so accidental `init claude` won't parse as something install-like.
**Migration**: Users who typed `spexl init claude` get a standard argparse error. The install help text covers the correct invocation.
