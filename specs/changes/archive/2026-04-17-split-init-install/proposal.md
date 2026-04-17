# Proposal: Split init into init + install

## Why

Today `spexl init` wears two hats: it scaffolds the project (`.spexl.toml` + `specs/`) and it installs agent integration assets (skills, subagents, hooks). Those jobs have different lifecycles – scaffolding happens once per project, while agent install is re-run to refresh assets and is repeated per agent target. Users invoking `spexl init` have to read the docs to figure out which behavior they'll get based on config state. Splitting them makes each command do exactly one thing.

## What Changes

- **BREAKING** `spexl init <target>` no longer installs agent assets. Use `spexl install <target>` instead.
- **BREAKING** `spexl init --remove` is removed. Use `spexl install --remove` to remove agent assets.
- `spexl init` (no args) now only scaffolds the project (creates `.spexl.toml` and `specs/` directory structure). Idempotent: re-running on a fully-initialized directory prints `spexl already initialized in this directory` to stderr and exits 0; partial states (missing config or missing specs dir) are backfilled.
- `spexl install <target>` installs agent integration files for the named target (initial: `claude`).
- `spexl install` (no args) refreshes every agent configured in `.spexl.toml`.
- `spexl install --remove` removes all spexl-managed agent files and strips `[agents]` from `.spexl.toml`. It does not touch `specs/` or `.spexl.toml` itself.
- The top-level help text distinguishes the two: `init` = project scaffold, `install` = agent assets.

## Capabilities

### Modified Capabilities

- `cli`: Adds `install` subcommand to the router; simplifies `init` to scaffold-only.
- `skill-generation`: Agent-asset installation moves from `init <target>` to `install <target>`; the scaffold-on-first-run behavior moves to `init`.

## Impact

- `src/spexl/cli/install.py` – splits `cmd_init` into `cmd_init` (scaffold only) and `cmd_install` (agent assets + refresh + remove). Registers two subparsers.
- `src/spexl/__init__.py` – help text and routing updated.
- `CLAUDE.md` – already describes `init` as installing skills/agents/hooks; update to reflect the split.
- `CHANGELOG.md` – add an entry noting the breaking rename.
- Existing users on zero-ver must switch `spexl init claude` invocations to `spexl install claude`. No deprecation shim (spexl is pre-1.0).

## Out of Scope

- Renaming the `skill-generation` capability (still accurate; the command name doesn't dictate the capability name).
- Changes to the onboarding primer (it doesn't mention `init`/`install`).
- New agent targets beyond `claude`.
