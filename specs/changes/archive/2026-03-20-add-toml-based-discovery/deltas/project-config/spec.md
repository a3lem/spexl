# Project Config

## Overview / Purpose

The `.spexl.toml` file marks a directory as a spexl project (or sub-project) and configures spec location, directory naming, and skill installation paths. Two discovery modes use this marker differently: spec discovery walks DOWN from cwd to find `.spexl.toml` files (you only see what's below you), while init/install_path resolution walks UP to find the nearest config.

## ADDED Requirements

### Requirement: Marker file format
The system SHALL recognize `.spexl.toml` as the project marker file. A minimal valid `.spexl.toml` is an empty file.

#### Scenario: Empty marker
- **GIVEN** a directory containing an empty `.spexl.toml`
- **WHEN** spexl resolves spec roots
- **THEN** the directory is recognized as a spec root with default settings (`specs_dir = "specs"`, `changes_dir = "changes"`, `reference_dir = "reference"`)

#### Scenario: Fully specified marker
- **GIVEN** a `.spexl.toml` containing:
  ```toml
  [specs_location]
  dir_path = "./design/specs"
  changes_dir = "proposals"
  reference_dir = "baseline"

  [agents.claude]
  install_path = ".claude"
  ```
- **WHEN** spexl resolves spec roots
- **THEN** the system looks for specs at `<toml_parent>/design/specs/`
- **AND** changes at `<toml_parent>/design/specs/proposals/`
- **AND** reference specs at `<toml_parent>/design/specs/baseline/`

### Requirement: Specs location defaults
The system SHALL use the following defaults when `[specs_location]` fields are omitted:

| Field | Default |
|-------|---------|
| `dir_path` | `"./specs"` |
| `changes_dir` | `"changes"` |
| `reference_dir` | `"reference"` |

#### Scenario: Partially specified location
- **GIVEN** a `.spexl.toml` containing only `[specs_location]` with `dir_path = "./design"`
- **WHEN** spexl resolves paths
- **THEN** specs are at `<toml_parent>/design/`
- **AND** changes at `<toml_parent>/design/changes/`
- **AND** reference at `<toml_parent>/design/reference/`

#### Scenario: No specs_location table
- **GIVEN** a `.spexl.toml` with no `[specs_location]` table
- **WHEN** spexl resolves paths
- **THEN** defaults are used: `specs/`, `specs/changes/`, `specs/reference/`

### Requirement: Install path inheritance
The system SHALL resolve `install_path` by walking UP from the current directory to find the nearest `.spexl.toml` that declares `[agents.<name>].install_path`. This walk-up is used only for init and agent installation, not for spec discovery. The `install_path` is relative to the toml file that declares it.

#### Scenario: Leaf inherits from root
- **GIVEN** a monorepo with:
  - `monorepo/.spexl.toml` containing `[agents.claude] install_path = ".claude"`
  - `monorepo/services/api/.spexl.toml` with no `[agents]` section
- **WHEN** spexl resolves the install path for `services/api/`
- **THEN** the install path resolves to `monorepo/.claude/`

#### Scenario: Leaf overrides root
- **GIVEN** a monorepo with:
  - `monorepo/.spexl.toml` containing `[agents.claude] install_path = ".claude"`
  - `monorepo/services/api/.spexl.toml` containing `[agents.claude] install_path = ".claude"`
- **WHEN** spexl resolves the install path for `services/api/`
- **THEN** the install path resolves to `monorepo/services/api/.claude/`

#### Scenario: No install path anywhere
- **GIVEN** a `.spexl.toml` with no `[agents]` section and no ancestor toml with one
- **WHEN** spexl attempts to resolve the install path
- **THEN** the system errors with a message indicating no install path is configured

### Requirement: Walk-up boundary
For init and agent installation, the system SHALL walk up and stop when it encounters a `.spexl.toml` that declares `install_path` for the requested agent, OR when it reaches a `.git` directory (repository root), whichever comes first. Spec discovery (`changes`, `refs`, `validate`) does not walk up.

#### Scenario: Stop at install_path
- **GIVEN** two `.spexl.toml` files in the ancestor chain, both with `install_path`
- **WHEN** spexl walks up from a leaf
- **THEN** it stops at the nearest ancestor with `install_path`

#### Scenario: Stop at git boundary
- **GIVEN** a `.spexl.toml` without `install_path` and no ancestor toml within the same git repo
- **WHEN** spexl walks up
- **THEN** it stops at the directory containing `.git`
- **AND** does not cross into parent repositories
