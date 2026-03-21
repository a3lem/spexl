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
│   ├── generate.py      # init (install, refresh, remove)
│   └── steering.py      # prime, explain, template
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

<!-- UNCHANGED: CLI entry point, Template resolution, Subcommand routing, Version flag,
     Recursive discovery by default, Changes archived filter, Changes linked filter,
     Computed status, New command skip flag, Validate skip values -->
