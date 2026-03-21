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
- **WHEN** the user runs `spexl new <slug>`, `spexl changes`, `spexl validate`, `spexl archive`, `spexl info`, `spexl refs`, `spexl link`, `spexl unlink`, or `spexl archived`
- **THEN** the behavior is identical to the current `spectl` implementation

### Requirement: Package structure
The system SHALL be structured as a Python package under `src/spexl/` with the following layout:

```
src/spexl/
├── __init__.py          # main() entry point, top-level argparse
├── errors.py            # SpexlError
├── specroot.py          # Spec root discovery, change resolution, .change.json I/O
├── cli/
│   ├── changes.py       # new, changes, archived, info, archive
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

#### Scenario: Install via uv tool install
- **WHEN** a user runs `uv tool install spexl`
- **THEN** the `spexl` command is available on PATH
- **AND** template files are accessible via `importlib.resources` from the `templates/` directory

### Requirement: Template resolution
The system SHALL resolve templates and partials from the package's `templates/` directory using `importlib.resources`, not filesystem paths relative to the script.

#### Scenario: Access a partial
- **WHEN** any spexl command needs a partial (e.g., rules, cross-phase context)
- **THEN** it reads from `spexl.templates.partials` via `importlib.resources`

#### Scenario: Access an artifact template
- **WHEN** any spexl command needs an artifact template (e.g., proposal.md)
- **THEN** it reads from `spexl.templates.artifacts` via `importlib.resources`

## ADDED Requirements

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
