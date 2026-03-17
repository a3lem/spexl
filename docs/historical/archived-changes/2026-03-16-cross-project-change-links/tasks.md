## 1. Helpers

- [x] Add `derive_spec_root(change_path)` -- returns `change_path.parent.parent`
- [x] Add `resolve_link(spec_root, link)` -- scans target specs dir for matching change ID, returns `(change_path, change_json)` or `None`

## 2. New commands

- [x] Add `link` subparser: two positional `change_path` arguments
- [x] Implement `cmd_link` -- resolve both paths, read both `.change.json`, compute relative specs paths, write link entries to both sides (idempotent)
- [x] Add `unlink` subparser: two positional `change_path` arguments
- [x] Implement `cmd_unlink` -- resolve both paths, remove link entries from both sides (idempotent), remove `links` key entirely when array becomes empty

## 3. Extend existing commands

- [x] `cmd_info`: resolve links via `resolve_link`, add to info dict, extend `format_info` for human-readable and JSON output (resolved + broken)
- [x] `cmd_archive`: after sync summary, resolve links and print warning for active/broken linked changes (non-blocking)
- [x] `validate_change`: check each link resolves (broken link error), check back-link exists (asymmetric link error), `--fix` adds missing back-links

## 4. Verification

- [x] Tests for requirement: link-changes
- [x] Tests for requirement: unlink-changes
- [x] Tests for requirement: validate-links
- [x] Tests for requirement: change-info (link scenarios)
- [x] Tests for requirement: archive-change (link scenarios)
- [x] Tests for requirement: validate-changes (link scenarios)

## 5. Correctness check

- [x] Create a mock monorepo with two specs dirs, two changes, run full workflow: `link` → `info` → `validate` → `archive` (with and without companion archived) → `validate` again after archive

## Notes

- No existing test suite. Tests will be new pytest files under `tests/`.
- `validate_change` currently receives `(change_path, fix, issues, fixed, archived=False)`. The link checks need access to the spec root (to resolve relative paths). The caller in `cmd_validate` has `root` available -- pass it through.
