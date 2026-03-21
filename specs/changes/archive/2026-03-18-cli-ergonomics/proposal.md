## Why

Several CLI commands lack consistent behavior: recursive discovery only works on `changes`, `--dir` semantics are ambiguous, and `archived` is a standalone subcommand when it's really a view filter on `changes`. These inconsistencies add friction for the primary users -- AI agents running spexl in monorepo contexts.

## What Changes

- **Recursive by default**: all listing commands (`changes`, `refs`, `validate`) walk from cwd by default. `--no-recurse` restricts to a single spec root.
- **Rename `--dir` to `--cwd`**: clarifies semantics -- overrides the discovery root, not the spec directory itself. spexl appends `/specs` internally.
- **Fold `archived` into `changes`**: `spexl changes` shows active only (default), `--archived` shows archived only, `--all` shows both. The standalone `archived` subcommand is removed.
- **Add `--linked` filter to `changes`**: show only changes that participate in cross-project links.
- **Add `links` listing**: surface all linked change bundles. Implemented as `spexl changes --linked` rather than a separate subcommand.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `cli`: recursive default, `--cwd` flag, fold `archived` into `changes`, add `--linked` filter

## Impact

- `__init__.py`: remove special-case routing for recursive changes; all listing commands handle their own discovery
- `specroot.py`: `resolve_spec_root` reads `--cwd` instead of `--dir`, appends `specs/`; `find_all_spec_roots` generalized to discover `reference/` dirs too
- `cli/changes.py`: absorb `archived` logic, add `--archived`/`--all`/`--linked` flags, recursive by default with `--no-recurse`
- `cli/refs.py`: add recursive discovery (default) and `--no-recurse`
- `cli/validate.py`: add recursive discovery (default) and `--no-recurse`
- `cli/links.py`: no new subcommand needed; listing covered by `changes --linked`
- **BREAKING**: `spexl archived` removed (replaced by `spexl changes --archived`). `--dir` renamed to `--cwd`.
