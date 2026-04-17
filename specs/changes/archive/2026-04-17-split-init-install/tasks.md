# Tasks

## CLI wiring

- [x] Split `cmd_init` in `src/spexl/cli/install.py` into two handlers: `cmd_init` (scaffold only) and `cmd_install` (agent install / refresh / remove)
- [x] Register both `init` and `install` subparsers from the `install` module
- [x] Update top-level help text so `init` reads "Scaffold a spexl project" and `install` reads "Install or refresh spexl agent integration files"
- [x] Make `spexl init <anything>` error out with a hint to use `spexl install <target>`
- [x] Ensure `spexl install --remove` clears `[agents]` from `.spexl.toml` but leaves the file in place

## Docs

- [x] Update `CLAUDE.md`: `init` = project scaffold, `install` = agent assets
- [x] Add `CHANGELOG.md` entry under `## [Unreleased]`: breaking rename of `spexl init <target>` to `spexl install <target>`

## Verification

- [x] Tests for requirement: CLI entry point (init and install routing)
- [x] Tests for requirement: Init scaffolds project (idempotent, rejects target arg, parent detection)
- [x] Tests for requirement: Install command (target / no-target / unknown target / --remove / help)
- [x] Tests for requirement: Subcommand routing (install module registers both parsers)
- [x] Tests for requirement: Install target (install / refresh / no-target-no-config / unsupported / --remove)
- [x] Tests for requirement: Methodology skill (install claude installs how-to-use skill with references)
- [x] Tests for requirement: Agent generation (spec-critic and spec-sync installed under the new command)
