## 1. Rename `--dir` to `--cwd`

- [x] Update `__init__.py`: rename `--dir` argument to `--cwd`, update help text
- [x] Update `specroot.py`: `resolve_spec_root` reads `args.cwd`, appends `/specs`
- [x] Update any other references to `args.dir`

## 2. Recursive by default

- [x] Generalize `find_all_spec_roots()` to discover dirs containing `reference/` or `changes/`
- [x] `cmd_changes`: make recursive the default path, add `--no-recurse` flag
- [x] `cmd_refs`: add recursive discovery as default, add `--no-recurse`
- [x] `cmd_validate`: add recursive discovery as default, add `--no-recurse`
- [x] Remove special-case routing in `__init__.py` (lines 65-67)

## 3. Fold `archived` into `changes`

- [x] Add `--archived` and `--all` flags to `changes` subparser (mutually exclusive group)
- [x] Update `cmd_changes` to handle archived/all filtering
- [x] Remove `p_archived` subparser and `cmd_archived` function
- [x] Remove `archived` import/registration from `__init__.py` if separate

## 4. Add `--linked` filter

- [x] Add `--linked` flag to `changes` subparser
- [x] Filter changes to those with non-empty `links` in `.change.json`
- [x] Ensure composability with `--archived` and `--all`

## 5. Verification

- [x] Tests for requirement: recursive discovery by default
- [x] Tests for requirement: changes archived filter
- [x] Tests for requirement: changes linked filter
- [x] Tests for requirement: CLI entry point (removed `archived` subcommand)
- [x] Tests for requirement: `--cwd` flag replaces `--dir`
- [x] Run full test suite, confirm no regressions
