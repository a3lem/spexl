## 1. Config infrastructure

- [x] Add `find_config()` walk-up discovery function
- [x] Add `write_config()` hand-written TOML writer
- [x] Add `read_config()` using `tomllib`

## 2. Managed file registry

- [x] Extract `_managed_files()` function returning `dict[Path, Callable[[], str]]`
- [x] Refactor current init to use registry for file generation

## 3. Rewrite init

- [x] Make `target` argument optional (`nargs="?"`)
- [x] Add `--remove` flag
- [x] Implement fresh install path (no config found + target given)
- [x] Implement idempotent refresh path (config found, content-hash comparison)
- [x] Implement no-target refresh path (reads config, refreshes all targets)
- [x] Implement `--remove` path (delete managed files + config, prune empty dirs)
- [x] Drop `specs/` directory creation from init

## 4. Remove update command

- [x] Delete `cmd_update` function from `generate.py`
- [x] Remove `update` subparser registration from `generate.register()`
- [x] Remove `generate.cmd_update` from `no_root_commands` in `__init__.py`
- [x] Delete `_extract_version()` (no longer needed)

## 5. Output formatting

- [x] Per-file status lines (unchanged/changed/created/removed)
- [x] Summary line with counts

## 6. Verification

- [x] Tests for config creation on fresh init
- [x] Tests for idempotent refresh (no changes)
- [x] Tests for idempotent refresh (content changed)
- [x] Tests for no-target refresh via config
- [x] Tests for `--remove`
- [x] Tests for `--remove` with no config
- [x] Tests for subdirectory walk-up discovery
- [x] Tests for unknown target
- [x] Tests for no target and no config
- [x] Existing compose tests still pass
