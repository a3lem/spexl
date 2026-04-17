# Onboarding

## MODIFIED Requirements

### Requirement: Onboard command
The system SHALL support `spexl onboard` to print a short primer intended for manual paste into a project's AGENTS.md or CLAUDE.md. The primer names the five action skills, the methodology skill (`spexl-foundations`), and the core rules, and points at the methodology skill for deeper knowledge. The command writes the primer content to stdout and a paste-instruction header to stderr, so that redirection (`spexl onboard >> AGENTS.md`) captures only the primer.

#### Scenario: Default output
- **WHEN** the user runs `spexl onboard`
- **THEN** the system prints the primer to stdout containing: a one-line statement that specs are the source of truth, the five action skills with their trigger phrases, the core rules, the directory layout, and a pointer to the `spexl-foundations` skill
- **AND** the system prints a paste-instruction header to stderr telling the user to add the content to AGENTS.md or CLAUDE.md
- **AND** exits 0

#### Scenario: Piped to AGENTS.md
- **WHEN** the user runs `spexl onboard >> AGENTS.md` (stdout redirected)
- **THEN** only the primer content is appended to AGENTS.md
- **AND** the paste-instruction header appears in the terminal (via stderr)

#### Scenario: Onboard does not install files
- **WHEN** the user runs `spexl onboard`
- **THEN** the system does NOT write any files on disk
- **AND** does NOT modify `.spexl.toml` or any other project file
