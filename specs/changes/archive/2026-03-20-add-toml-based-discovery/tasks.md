## 1. Config module

- [x] Create `src/spexl/config.py` with `SpecsLocation` and `ProjectConfig` dataclasses
- [x] Implement `ProjectConfig.from_toml(path)` with defaults for missing fields
- [x] Implement `find_project_root(start)` – walk up for `.spexl.toml`, stop at `install_path` or `.git`
- [x] Implement `discover_all_configs(root)` – walk down from root, skip noise dirs, return `list[ProjectConfig]`
- [x] Implement config writing (`write_config`, `update_config`) moved from generate.py
- [x] Add resolved path properties: `specs_dir`, `changes_path`, `reference_path`

## 2. Rewire discovery in specroot.py

- [x] Replace `find_all_spec_roots()` with call to `config.discover_all_configs()`
- [x] Replace `resolve_spec_root(args)` with call to `config.find_project_root()`
- [x] Update `discover_changes` to accept a `Path` for the changes dir (no longer hardcoded)
- [x] Update `discover_archived` similarly
- [x] Update `resolve_change` to accept a `Path` for the changes dir
- [x] Remove `derive_spec_root` (replaced by `config.toml_path.parent`)

## 3. Update CLI commands to use config

- [x] `cmd_changes`: use `ProjectConfig` list, read `changes_path` from each config
- [x] `cmd_refs`: use `ProjectConfig` list, read `reference_path` from each config
- [x] `cmd_validate`: use `ProjectConfig` list, add `.spexl.toml` validity checks
- [x] `cmd_new`: resolve root from config, use `changes_path`
- [x] `cmd_info`: resolve root from config, use `changes_path`
- [x] `cmd_archive`: resolve root from config, use `changes_path` and `reference_path`
- [x] `__init__.py`: pass `--cwd` as start directory for walk-up in all code paths

## 4. Update generate.py

- [x] Remove `_find_config`, `_read_config`, `_write_config`, `_update_config` – import from config.py
- [x] `spexl init` (no args, no existing toml): create `.spexl.toml` + `specs/{changes,reference}/`
- [x] `spexl init` (no args, existing toml): error with "already initialized"
- [x] `spexl init claude`: existing behavior, unchanged
- [x] `_write_config` gains `[specs_location]` support (write only non-default values)

## 5. Tests

- [x] `test_config.py`: parsing, defaults, empty file, partial specs_location, full specs_location
- [x] `test_config.py`: walk-up finds nearest toml, stops at `.git`, stops at `install_path`
- [x] `test_config.py`: walk-down finds all `.spexl.toml`, skips noise dirs
- [x] Update `test_discovery.py`: fixtures create `.spexl.toml` markers, false positive dirs ignored
- [x] Update `conftest.py`: `spec_root` fixture creates `.spexl.toml`
- [x] Update all command tests that rely on bare `specs/` directory fixtures
- [x] Test `spexl init` project scaffolding (new and idempotent cases)
- [x] Test custom `specs_location` names flow through to `changes`, `refs`, `validate`

## Notes

Phases 1-2 are the core – once config.py exists and specroot.py delegates to it, the rest is mechanical. Phase 3 is repetitive but straightforward (search-and-replace hardcoded paths with config properties). Phase 4 is mostly deletion. Phase 5 should be done incrementally alongside each phase, not saved for the end.
