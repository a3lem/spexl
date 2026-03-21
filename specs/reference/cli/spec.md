# CLI

## Overview / Purpose

The `spexl` command-line interface routes user invocations to subcommand handlers across plumbing, skill generation, and runtime steering capabilities. It is structured as a Python package under `src/spexl/` and distributed via PyPI.

## Requirements

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

### Requirement: Init scaffolds project
The system SHALL support `spexl init` (no arguments) to create a `.spexl.toml` file and `specs/` directory structure in the current directory.

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

#### Scenario: Init with existing marker and agents configured
- **GIVEN** a directory with `.spexl.toml` containing an `[agents]` section
- **WHEN** the user runs `spexl init` with no target argument
- **THEN** the system refreshes all installed agents (overwrites files whose content differs)

#### Scenario: Init with existing marker and no agents
- **GIVEN** a directory with `.spexl.toml` containing no `[agents]` section
- **WHEN** the user runs `spexl init` with no target argument
- **THEN** the system prints an error suggesting `spexl init <target>`
- **AND** exits 1

#### Scenario: Init does not overwrite specs
- **GIVEN** a directory with no `.spexl.toml` but an existing `specs/` directory
- **WHEN** the user runs `spexl init`
- **THEN** the system creates `.spexl.toml`
- **AND** creates only missing subdirectories under `specs/`
- **AND** does not modify existing files

#### Scenario: Init agent setup remains separate
- **WHEN** the user runs `spexl init claude`
- **THEN** the system installs agent skills (existing behavior)

### Requirement: Validate checks marker
The system SHALL check for `.spexl.toml` presence and validity during `spexl validate`. Validate uses the same downward discovery as `changes` and `refs`.

#### Scenario: Missing marker
- **WHEN** the user runs `spexl validate` in a directory with no `.spexl.toml` below it
- **THEN** the system prints "All changes valid" (no specs to validate)
- **AND** exits 0

#### Scenario: Invalid TOML
- **GIVEN** a `.spexl.toml` with syntax errors
- **WHEN** the user runs `spexl validate`
- **THEN** the system reports the parse error with file path and line number

#### Scenario: Specs directory missing
- **GIVEN** a valid `.spexl.toml` with `dir_path = "./specs"`
- **WHEN** the configured `specs/` directory does not exist
- **THEN** `spexl validate` reports the missing directory

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

The global `--cwd` option sets the starting directory for `.spexl.toml` discovery. Default: current working directory.

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** template files are accessible via `importlib.resources` from the `templates/` directory

#### Scenario: Explicit project directory
- **WHEN** the user runs `spexl --cwd /path/to/project changes`
- **THEN** the system starts `.spexl.toml` discovery from `/path/to/project/`

#### Scenario: Default project directory
- **WHEN** the user runs `spexl changes` without `--cwd`
- **THEN** the system starts `.spexl.toml` discovery from the current working directory

### Requirement: Template resolution
The system SHALL resolve templates and partials from the package's `templates/` directory using `importlib.resources`, not filesystem paths relative to the script.

#### Scenario: Access a partial
- **WHEN** any spexl command needs a partial (e.g., rules, cross-phase context)
- **THEN** it reads from `spexl.templates.partials` via `importlib.resources`

#### Scenario: Access an artifact template
- **WHEN** any spexl command needs an artifact template (e.g., proposal.md)
- **THEN** it reads from `spexl.templates.artifacts` via `importlib.resources`

### Requirement: Subcommand routing
The system SHALL use argparse with subparsers to route to command handlers. Each CLI module (`changes`, `links`, `validate`, `refs`, `generate`, `steering`) exposes a `register(subparsers)` function called by `main()`.

#### Scenario: Help for a specific subcommand
- **WHEN** the user runs `spexl <subcommand> --help`
- **THEN** the system prints subcommand-specific usage and exits 0

### Requirement: Version flag
The system SHALL support `spexl --version` and print the version from package metadata.

#### Scenario: Print version
- **WHEN** the user runs `spexl --version`
- **THEN** the system prints the version string from pyproject.toml
- **AND** exits 0

### Requirement: Recursive discovery by default
The system SHALL discover spec roots by walking DOWN from the current directory (or `--cwd`) to find `.spexl.toml` marker files. Each `.spexl.toml` marks a spec root. Directories named `node_modules`, `.venv`, `.git`, `__pycache__`, and `archive` are excluded from the walk. Spec discovery never walks up -- it only sees what is below the starting directory. The `--no-recurse` flag switches to single-root resolution mode, which walks UP to find the nearest `.spexl.toml` (see project-config capability for walk-up boundary rules).

#### Scenario: Multiple spec roots in monorepo
- **GIVEN** a monorepo with `.spexl.toml` at the root and at `services/api/` and `services/billing/`
- **WHEN** the user runs `spexl changes` from the monorepo root
- **THEN** the system discovers all spec roots below and lists changes from each

#### Scenario: Single project
- **GIVEN** a project with a single `.spexl.toml` at the root
- **WHEN** the user runs `spexl changes`
- **THEN** the system discovers the single spec root and lists its changes

#### Scenario: Subdirectory without marker does not walk up
- **GIVEN** a project with `.spexl.toml` and specs at the root
- **WHEN** the user runs `spexl changes` from a subdirectory (e.g., `src/`) that has no `.spexl.toml` below it
- **THEN** the system prints "No changes"
- **AND** does not show the parent's specs

#### Scenario: Subdirectory scoping in monorepo
- **GIVEN** a monorepo with spec roots at `proj-a/` and `proj-b/`
- **WHEN** the user runs `spexl changes` from `proj-a/`
- **THEN** only `proj-a`'s changes are listed
- **AND** `proj-b`'s changes are not shown

#### Scenario: No marker file found
- **WHEN** the user runs `spexl changes` in a directory with no `.spexl.toml` below it
- **THEN** the system prints "No changes"
- **AND** exits 0

#### Scenario: No-recurse flag
- **WHEN** the user runs `spexl changes --no-recurse`
- **THEN** the system switches to single-root resolution: walks UP to find the nearest `.spexl.toml`
- **AND** lists changes from that single spec root only
- **AND** does not walk down to find sibling spec roots

#### Scenario: False positive prevention
- **GIVEN** a directory tree containing `docs/changes/some-subdir/` and `node_modules/pkg/reference/`
- **WHEN** the user runs `spexl changes`
- **THEN** neither `docs/` nor `node_modules/` appears as a spec root
- **AND** only directories with `.spexl.toml` markers are recognized

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

### Requirement: Changes linked filter
The system SHALL support `spexl changes --linked` to show only changes that have entries in their `.change.json` `links` field.

#### Scenario: Filter to linked changes
- **GIVEN** three active changes, one of which has a non-empty `links` array in `.change.json`
- **WHEN** the user runs `spexl changes --linked`
- **THEN** only the linked change is listed

#### Scenario: Compose with archived
- **WHEN** the user runs `spexl changes --linked --archived`
- **THEN** only archived changes that have links are listed

### Requirement: Computed status
The system SHALL compute a status for each active change based on which artifacts are present and the state of the task checklist. The `.change.json` file MAY contain a `skip` field listing artifacts that are intentionally omitted.

#### Scenario: All artifacts present, no tasks started
- **GIVEN** a change with proposal.md, design.md, tasks.md, and at least one delta spec
- **WHEN** no tasks are checked
- **THEN** the computed status is "ready"

#### Scenario: All artifacts present, some tasks done
- **GIVEN** a change with all artifacts present
- **WHEN** at least one task is checked and at least one is unchecked
- **THEN** the computed status is "in progress"

#### Scenario: All artifacts present, all tasks done
- **GIVEN** a change with all artifacts present
- **WHEN** all tasks are checked
- **THEN** the computed status is "complete"

#### Scenario: Missing artifact without skip
- **GIVEN** a change missing design.md or tasks.md
- **WHEN** the missing artifact is NOT listed in `.change.json` `skip`
- **THEN** the computed status is "drafting"

#### Scenario: Missing artifact with skip
- **GIVEN** a change missing design.md
- **WHEN** `.change.json` contains `"skip": ["design"]`
- **THEN** the status computation treats design as present
- **AND** the computed status advances past "drafting" if all other conditions are met

#### Scenario: Skip design and tasks
- **GIVEN** a change with only proposal.md and at least one delta spec
- **WHEN** `.change.json` contains `"skip": ["design", "tasks"]`
- **THEN** the computed status is "complete" (no task checklist to evaluate)

### Requirement: New command skip flag
The system SHALL support `spexl new <slug> --skip <artifact>` to write a skip list into `.change.json` at creation time. The flag can be repeated.

#### Scenario: New with skip
- **WHEN** the user runs `spexl new my-change --skip design --skip tasks`
- **THEN** `.change.json` contains `"skip": ["design", "tasks"]`

#### Scenario: New without skip
- **WHEN** the user runs `spexl new my-change` with no --skip flag
- **THEN** `.change.json` does not contain a `skip` field

### Requirement: Validate skip values
The system SHALL validate that the `skip` field in `.change.json` contains only `design` and/or `tasks`. Other values are invalid.

#### Scenario: Invalid skip value
- **GIVEN** a `.change.json` with `"skip": ["proposal"]`
- **WHEN** the user runs `spexl validate`
- **THEN** the system reports an error for the invalid skip value
- **AND** exits 1

#### Scenario: Valid skip value
- **GIVEN** a `.change.json` with `"skip": ["design"]`
- **WHEN** the user runs `spexl validate`
- **THEN** no skip-related errors are reported
