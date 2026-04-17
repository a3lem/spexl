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
├── cli/
│   ├── changes.py       # new, changes, info, archive
│   ├── links.py         # link, unlink
│   ├── validate.py      # validate (+ --fix)
│   ├── refs.py          # refs
│   ├── install.py       # init (scaffold), install (agent assets)
│   └── steering.py      # onboard
└── content/             # Package data: skills, agents, onboard primer
    ├── skills/
    │   ├── spexl-foundations/              # methodology skill with references/
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
