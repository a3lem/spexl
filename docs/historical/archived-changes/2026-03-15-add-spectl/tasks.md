## Scaffolding

- [x] Create `scripts/spectl.py` with argparse skeleton and command dispatch
- [x] Implement `SpectlError` + top-level error handling
- [x] Implement spec root discovery (`resolve_spec_root`, `--dir`)
- [x] Implement `output()` helper with `--json` support

## Commands

- [x] `spectl new` -- create change directory, `.change.json`, `deltas/`
- [x] `spectl changes` -- list active changes with computed status
- [x] `spectl archived` -- list archived changes with reason
- [x] `spectl info` -- computed overview (artifacts, deltas, task counts, archived status)
- [x] `spectl archive` -- sync summary, move to archive, set `archived` field
- [x] `spectl archive --rejected` -- archive with reason `rejected`, skip sync summary
- [x] `spectl archive --force` -- override incomplete tasks guard
- [x] `spectl archive --dry-run` -- print sync summary without moving
- [x] `spectl refs` -- list reference specs
- [x] `spectl validate` -- check changes for structural problems
- [x] `spectl validate --fix` -- repair fixable issues (missing id, created)

## Cross-cutting

- [x] Identifier resolution (slug, id, or path)
- [x] `--archived` flag on `info` to scan archive
- [x] Computed status (`drafting`, `ready`, `in progress`, `complete`)
- [x] Sync summary parsing (regex-based heading counts)
- [x] Incomplete tasks guard on archive

## Integration

- [x] Add `spectl` section to CLAUDE.md
- [x] Update design.md to match implementation
- [x] Update spec to match implementation (computed status, command renames)
