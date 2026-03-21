# CLI

## ADDED Requirements

### Requirement: Recursive discovery by default
The system SHALL recursively walk from the working directory to discover all spec roots when running `changes`, `refs`, or `validate`. A spec root is a directory containing a `reference/` or `changes/` subdirectory.

#### Scenario: Multiple spec roots in monorepo
- **WHEN** the user runs `spexl changes` from a monorepo root containing `packages/a/specs/` and `packages/b/specs/`
- **THEN** the system discovers both spec roots and lists changes from each

#### Scenario: Single project
- **WHEN** the user runs `spexl changes` from a project with only `./specs/`
- **THEN** the system discovers the single spec root and lists its changes

#### Scenario: No-recurse flag
- **WHEN** the user runs `spexl changes --no-recurse`
- **THEN** the system only looks in `--cwd` (or cwd) for a `specs/` directory
- **AND** does not walk subdirectories

### Requirement: Changes linked filter
The system SHALL support `spexl changes --linked` to show only changes that have entries in their `.change.json` `links` field.

#### Scenario: Filter to linked changes
- **GIVEN** three active changes, one of which has a non-empty `links` array in `.change.json`
- **WHEN** the user runs `spexl changes --linked`
- **THEN** only the linked change is listed

#### Scenario: Compose with archived
- **WHEN** the user runs `spexl changes --linked --archived`
- **THEN** only archived changes that have links are listed

### Requirement: Changes archived filter
The system SHALL support `spexl changes --archived` to list only archived changes, and `spexl changes --all` to list both active and archived changes. Without either flag, only active changes are shown.

#### Scenario: Default shows active only
- **WHEN** the user runs `spexl changes`
- **THEN** only active (non-archived) changes are listed

#### Scenario: Archived flag
- **WHEN** the user runs `spexl changes --archived`
- **THEN** only archived changes are listed

#### Scenario: All flag
- **WHEN** the user runs `spexl changes --all`
- **THEN** both active and archived changes are listed

#### Scenario: Archived and all are mutually exclusive
- **WHEN** the user runs `spexl changes --archived --all`
- **THEN** the system prints an error and exits 1

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

#### Scenario: Invoke removed subcommand
- **WHEN** the user runs `spexl archived`
- **THEN** the system prints an error with the unknown command name
- **AND** exits 1

### Requirement: Subcommand routing
The system SHALL use argparse with subparsers to route to command handlers. Each CLI module (`changes`, `links`, `validate`, `refs`, `generate`, `steering`) exposes a `register(subparsers)` function called by `main()`.

#### Scenario: Help for a specific subcommand
- **WHEN** the user runs `spexl <subcommand> --help`
- **THEN** the system prints subcommand-specific usage and exits 0

## REMOVED Requirements

### Requirement: Standalone archived subcommand
**Reason**: Folded into `changes --archived`. A separate subcommand doesn't carry its weight -- same data shape, same output format.
**Migration**: Use `spexl changes --archived` instead of `spexl archived`.

## MODIFIED Requirements

### Requirement: Package structure
The system SHALL be structured as a Python package under `src/spexl/` with the following layout:

```
src/spexl/
├── __init__.py          # main() entry point, top-level argparse
├── errors.py            # SpexlError
├── specroot.py          # Spec root discovery, change resolution, .change.json I/O
├── cli/
│   ├── changes.py       # new, changes, info, archive
│   ├── links.py         # link, unlink
│   ├── validate.py      # validate (+ --fix)
│   ├── refs.py          # refs
│   ├── generate.py      # init, update
│   └── steering.py      # context, template
├── generate/
│   └── compose.py       # Skill composition logic
├── templates/           # Package data: partials, actions, agents, concepts, artifacts
│   ├── partials/
│   ├── actions/
│   ├── agents/
│   ├── concepts/
│   └── artifacts/
└── templates.py         # importlib.resources access to templates/
```

The global `--cwd` option specifies the project directory. spexl appends `/specs` internally to locate the spec root. Default: current working directory.

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** template files are accessible via `importlib.resources` from the `templates/` directory

#### Scenario: Explicit project directory
- **WHEN** the user runs `spexl --cwd /path/to/project changes`
- **THEN** the system looks for specs at `/path/to/project/specs/`

#### Scenario: Default project directory
- **WHEN** the user runs `spexl changes` without `--cwd`
- **THEN** the system uses the current working directory as the project root
