## Why

`spexl init` and `spexl update` are artificially split. Init refuses to run when skills exist, update uses version-based drift detection that misses content changes. There's no way to remove installed files. The command also incorrectly creates `specs/` directories (should be lazy) and doesn't guard against nested installations.

## What Changes

- **`spexl init claude` becomes idempotent** – always writes latest content, compares by content hash not version. First run creates, subsequent runs refresh. No separate `update` command. **BREAKING**: `spexl update` is removed.
- **`.spexl.toml` config file** – created on first init at project root. Stores `[agents.claude]` with `install_path` (where skills/agents/rules were written). Subsequent `spexl init` (no target arg) reads this to know what to refresh.
- **`spexl init --remove`** – removes all spexl-managed files under the install path (skills, agents, rules). Never touches `specs/`. Only operates on the current directory's install, no recursion.
- **Subdirectory guard** – `spexl init claude` walks up to find an existing `.spexl.toml`. If found with an `install_path`, updates that installation instead of creating a new one.
- **No more `specs/` creation** – init no longer creates `specs/reference/` and `specs/changes/`. That happens lazily when `spexl new` is first run.

## Capabilities

### New Capabilities

- `project-config`: `.spexl.toml` file at project root storing agent targets and install paths

### Modified Capabilities

- `skill-generation`: init becomes idempotent, update is removed, --remove added, specs/ creation removed
- `cli`: remove `update` subcommand, add `--remove` flag to `init`

## Impact

- `src/spexl/cli/generate.py` – rewrite init, remove update, add --remove
- `src/spexl/__init__.py` – remove update subcommand registration
- `.spexl.toml` – new file created by init
- Tests – rewrite generate tests for new behavior
