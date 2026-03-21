## Why

Spec discovery uses `rglob("changes")` / `rglob("reference")` to find spec roots. This produces false positives (any directory named `changes/` with subdirectories gets treated as a spec root), misses specs when running from subdirectories (no upward walk), and silently ignores `--cwd` in recursive mode. A `.spexl.toml` marker file replaces heuristic scanning with explicit declaration.

## What Changes

- `.spexl.toml` becomes the sole mechanism for spec root discovery. Its presence marks "specs live here."
- Discovery walks UP from cwd (or `--cwd`) to find the nearest `.spexl.toml`, then UP further to find the project root (a `.spexl.toml` with `install_path`, or the topmost one before a `.git` boundary). From the root, walks DOWN to find all `.spexl.toml` files in the tree.
- `--cwd` sets the starting directory for the upward walk. It is no longer silently ignored in recursive mode.
- The `[specs_location]` table in `.spexl.toml` configures where specs live relative to the marker, and what the `changes/` and `reference/` subdirectories are named. All three default if omitted.
- `spexl init` (without arguments) creates `.spexl.toml` + the `specs/` directory structure. Agent setup (`spexl init claude`) remains a separate step.
- Without a `.spexl.toml`, spexl errors with a message suggesting `spexl init`. No legacy fallback.

## Capabilities

### New Capabilities

- `project-config`: The `.spexl.toml` file format, its fields, defaults, and the inheritance model for `install_path`.

### Modified Capabilities

- `cli`: Discovery algorithm changes (walk-up + walk-down via `.spexl.toml` instead of `rglob`). `--cwd` semantics change. `spexl init` gains project scaffolding. `--no-recurse` behavior changes.

## Impact

- `specroot.py`: `find_all_spec_roots()` and `resolve_spec_root()` rewritten to use `.spexl.toml` discovery.
- `cli/changes.py`, `cli/refs.py`, `cli/validate.py`: All recursive commands pass `--cwd` through to discovery.
- `cli/generate.py`: `spexl init` (no args) creates `.spexl.toml` + `specs/` structure.
- All hardcoded `"changes"` / `"reference"` string literals replaced with values read from `.spexl.toml`.
- Existing projects need a `.spexl.toml` file added (one-time migration via `spexl init`).
- Tests: discovery tests rewritten around `.spexl.toml` fixtures instead of bare directory structures.
