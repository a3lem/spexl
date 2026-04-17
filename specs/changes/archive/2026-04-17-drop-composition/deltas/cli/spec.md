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
│   ├── generate.py      # init (copies spexl.content tree verbatim)
│   └── steering.py      # onboard
├── generate/
│   └── __init__.py      # empty; composition machinery removed
└── content/             # Package data: skills, agents, onboard primer
    ├── skills/
    │   ├── learn-about-sdd-with-spexl/     # librarian with references/
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
    │   ├── spec-critic.md
    │   └── spec-sync.md
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

## REMOVED Requirements

### Requirement: Template resolution
**Reason**: Template resolution was the mechanism that served `spexl explain`, `spexl template`, and skill composition. All three consumers are removed by this change. Skills are now served as a verbatim tree copy by `spexl init`; methodology knowledge is served by the librarian skill's `references/` files; artifact scaffolding is no longer a CLI affordance.

**Migration**: Code that read from `spexl.templates.partials`, `spexl.templates.artifacts`, or any other `spexl.templates` subpackage must be rewritten to read from `spexl.content` (via `importlib.resources.files("spexl.content")`) or removed. The package `spexl.templates` no longer exists.
