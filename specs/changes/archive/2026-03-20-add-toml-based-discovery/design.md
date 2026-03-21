# Design

## Context

Spec discovery currently lives in two places that don't talk to each other:
- `specroot.py` has `find_all_spec_roots()` (rglob for `changes/`/`reference/` dirs) and `resolve_spec_root()` (hardcoded `specs/` lookup)
- `generate.py` has `_find_config()` (walk-up for `.spexl.toml`)

Both solve parts of the discovery problem but neither solves it fully. The rglob approach produces false positives and can't walk up. The config walk-up in generate.py only finds one root and isn't used by any plumbing commands.

## Goals / Non-Goals

**Goals:**
- Single discovery mechanism based on `.spexl.toml` markers, used by all commands
- Walk-up from cwd (or `--cwd`) to anchor in a project, walk-down to find all spec roots
- Configurable spec directory names via `[specs_location]`
- `spexl init` (no args) creates `.spexl.toml` + `specs/` structure

**Non-goals:**
- Backwards compatibility with projects that have no `.spexl.toml`
- Workspace/member listing in root toml (rglob for `.spexl.toml` is sufficient)
- TOML writing library (hand-format like `_write_config` already does)

## Decisions

### 1. New `config.py` module for TOML parsing and project resolution

Extract `.spexl.toml` handling from `generate.py` into `src/spexl/config.py`. This module owns:
- Parsing `.spexl.toml` into a typed dataclass
- Walking up to find markers (reusing `_find_config` logic from generate.py)
- Walking down to find all markers in a project tree
- Resolving `specs_location` defaults

```python
@dataclass
class SpecsLocation:
    dir_path: str = "./specs"
    changes_dir: str = "changes"
    reference_dir: str = "reference"

@dataclass
class ProjectConfig:
    toml_path: Path
    specs_location: SpecsLocation
    agents: dict[str, dict[str, str]]  # e.g. {"claude": {"install_path": ".claude/"}}
```

`ProjectConfig.from_toml(path)` parses the file, applying defaults for missing fields. An empty `.spexl.toml` produces all defaults.

The resolved absolute paths:
- `specs_dir` → `toml_path.parent / specs_location.dir_path`
- `changes_dir` → `specs_dir / specs_location.changes_dir`
- `reference_dir` → `specs_dir / specs_location.reference_dir`

### 2. Two-phase discovery replaces both `find_all_spec_roots` and `resolve_spec_root`

**Phase 1 – walk up:** Starting from `--cwd` (or process cwd), walk parent directories looking for `.spexl.toml`. Stop at the first `.spexl.toml` that has `[agents.X].install_path`, or at the directory containing `.git`, whichever comes first. This identifies the project root.

If no `.spexl.toml` is found at all, error with: `No .spexl.toml found. Run 'spexl init' to initialize.`

**Phase 2 – walk down:** From the project root, glob for `**/.spexl.toml`. Skip directories named `node_modules`, `.venv`, `.git`, `__pycache__`, `archive`. Each found `.spexl.toml` is a spec root. Parse each to get its `specs_location`.

The walk-up finds the nearest `.spexl.toml` first (which may be a leaf). If that leaf has no `install_path`, continue walking up to find the root. The walk-down then starts from the root.

**`--no-recurse`:** Walk up only. Use the nearest `.spexl.toml` as the sole spec root. No walk-down.

### 3. `specroot.py` functions updated to accept `ProjectConfig`

Replace the current signatures:
- `find_all_spec_roots(base)` → `discover_spec_roots(start: Path | None = None) -> list[ProjectConfig]`
- `resolve_spec_root(args)` → absorbed into the walk-up phase

All callers (`cmd_changes`, `cmd_refs`, `cmd_validate`) switch from hardcoded `r / "changes"` and `r / "reference"` to `config.changes_dir` and `config.reference_dir` resolved from the `ProjectConfig`.

The `derive_spec_root(change_path)` helper is replaced by the config's `toml_path.parent`.

### 4. `generate.py` delegates to `config.py`

Remove `_find_config`, `_read_config`, `_write_config`, `_update_config` from generate.py. Replace with imports from `config.py`. The `_write_config` and `_update_config` functions move to config.py as well (they write `.spexl.toml`).

The `_write_config` function gains support for `[specs_location]` – it writes the table only when non-default values are provided.

### 5. `spexl init` (no args) scaffolds the project

When `spexl init` is called without a target argument and no `.spexl.toml` exists:
1. Create `.spexl.toml` with defaults (empty file or minimal content)
2. Create `specs/changes/` and `specs/reference/` directories
3. Print created paths

When `.spexl.toml` already exists and no target is given, the existing refresh behavior applies (refresh all installed agents).

This means `spexl init` becomes the entry point for new projects, and `spexl init claude` adds agent integration on top.

### 6. Hardcoded `"changes"` / `"reference"` strings removed from all modules

Every place that currently does `root / "changes"` or `root / "reference"` switches to reading from the config. This affects:
- `specroot.py`: `discover_changes`, `discover_archived`, `resolve_change`, `derive_spec_root`
- `cli/changes.py`: `cmd_changes`, `cmd_new`, `cmd_info`, `cmd_archive`
- `cli/refs.py`: `cmd_refs`
- `cli/validate.py`: `cmd_validate`

## Risks / Trade-offs

**[Config I/O without a TOML writer]** → Python's `tomllib` is read-only. Writing is done with string formatting (already the approach in generate.py). This is fine for the small surface area of `.spexl.toml` but means we hand-format. If the config grows complex, consider adding `tomli-w` as a dependency.

**[Walk-up performance]** → Walking up is bounded by directory depth (typically <20 levels). Walking down uses `rglob("*.toml")` which is faster than the current `rglob("changes")` + `rglob("reference")` (one glob instead of two, and `.spexl.toml` is rare). No performance concern.

**[Empty toml = valid]** → An empty file is a valid marker, which means an accidental `.spexl.toml` could confuse discovery. Acceptable because the filename is specific enough that accidental creation is unlikely.

## Open Questions

None.
