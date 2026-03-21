## ADDED Requirements

### Requirement: Config file
The system SHALL use `.spexl.toml` at the project root as the project-level configuration file. It is created by `spexl init` and read by subsequent spexl commands.

#### Scenario: Config created on init
- **GIVEN** no `.spexl.toml` exists in the current or any parent directory
- **WHEN** the user runs `spexl init claude`
- **THEN** `.spexl.toml` is created at the current working directory
- **AND** contains an `[agents.claude]` table with `install_path` set to the relative path where skills/agents/rules were written (e.g. `.claude`)

#### Scenario: Config with install_path
- **GIVEN** `.spexl.toml` contains `[agents.claude]` with `install_path = ".claude"`
- **WHEN** `spexl init` is run without a target argument
- **THEN** the system reads the config and refreshes the `claude` installation at the recorded path

#### Scenario: Config file format
- **WHEN** `.spexl.toml` is read
- **THEN** the file is valid TOML

### Requirement: Config discovery
The system SHALL walk up the directory tree from the current working directory to find `.spexl.toml`.

#### Scenario: Init from subdirectory with existing config
- **GIVEN** `.spexl.toml` exists at `/project/` with `[agents.claude]` and `install_path = ".claude"`
- **WHEN** the user runs `spexl init claude` from `/project/packages/web/`
- **THEN** the system finds `/project/.spexl.toml`
- **AND** updates the installation at `/project/.claude/`
- **AND** prints the resolved install path

#### Scenario: No config found during walk-up
- **GIVEN** no `.spexl.toml` exists in the current directory or any parent
- **WHEN** the user runs `spexl init claude`
- **THEN** the system creates `.spexl.toml` in the current working directory
- **AND** proceeds with installation
