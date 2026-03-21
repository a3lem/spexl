## MODIFIED Requirements

### Requirement: Recursive discovery by default
The system SHALL discover spec roots by walking DOWN from the current directory (or `--cwd`) to find `.spexl.toml` marker files. Each `.spexl.toml` marks a spec root. Directories named `node_modules`, `.venv`, `.git`, `__pycache__`, and `archive` are excluded from the walk. Spec discovery never walks up -- it only sees what is below the starting directory.

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
- **THEN** the system walks UP to find the nearest `.spexl.toml`
- **AND** lists changes from that single spec root only

#### Scenario: False positive prevention
- **GIVEN** a directory tree containing `docs/changes/some-subdir/` and `node_modules/pkg/reference/`
- **WHEN** the user runs `spexl changes`
- **THEN** neither `docs/` nor `node_modules/` appears as a spec root
- **AND** only directories with `.spexl.toml` markers are recognized

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

## ADDED Requirements

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
- **AND** prints a note indicating a parent project was found

#### Scenario: Init with existing marker
- **WHEN** the user runs `spexl init` in a directory that already has `.spexl.toml`
- **THEN** the system refreshes installed agents (if any are configured)

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
The system SHALL check for `.spexl.toml` presence and validity during `spexl validate`.

#### Scenario: Missing marker
- **WHEN** the user runs `spexl validate`
- **AND** no `.spexl.toml` is found
- **THEN** the system reports an error suggesting `spexl init`

#### Scenario: Invalid TOML
- **GIVEN** a `.spexl.toml` with syntax errors
- **WHEN** the user runs `spexl validate`
- **THEN** the system reports the parse error with file path and line number

#### Scenario: Specs directory missing
- **GIVEN** a valid `.spexl.toml` with `dir_path = "./specs"`
- **WHEN** the configured `specs/` directory does not exist
- **THEN** `spexl validate` reports the missing directory
