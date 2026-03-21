## 1. Package foundation

### 1.1 Entry point and routing

- [x] Rewrite `src/spexl/__init__.py` with `main()` that builds a top-level argparse parser with `--version`
- [x] Top-level parser creates shared `subparsers` object, passes it to each module's registration function
- [x] `--version` reads from `importlib.metadata.version("spexl")`
- [x] Unknown subcommand → print error + suggest `spexl --help`, exit 1
- [x] No subcommand → print usage summary, exit 0 (not exit 1 – unlike current spectl)

### 1.2 Shared modules

- [x] Create `src/spexl/errors.py` with `SpexlError` (renamed from `SpectlError`)
- [x] Create `src/spexl/specroot.py` with shared helpers extracted from `spectl.py`:
  - `resolve_spec_root(args)` – find the specs/ directory
  - `find_spec_roots(start)` – recursive discovery for monorepos
  - `resolve_change(identifier, root)` – resolve slug/id/path to change dir
  - `read_change_json(path)` / `write_change_json(path, data)` – .change.json I/O
  - `computed_status(change_path)` – derive status from filesystem
  - `generate_id()` – random ID generation

### 1.3 Port CLI commands into domain modules

- [x] Create `src/spexl/cli/changes.py` with `register(subparsers)`:
  - `cmd_new` – scaffold a new change
  - `cmd_changes` – list active changes (incl. `-r` recursive)
  - `cmd_archived` – list archived changes
  - `cmd_info` – show change overview
  - `cmd_archive` – archive a change (incl. `--dry-run`, `--rejected`, `--force`)
- [x] Create `src/spexl/cli/links.py` with `register(subparsers)`:
  - `cmd_link` – link two changes across spec roots
  - `cmd_unlink` – remove link between changes
  - (These don't use spec root discovery – they take explicit paths)
- [x] Create `src/spexl/cli/validate.py` with `register(subparsers)`:
  - `cmd_validate` – check changes for structural problems (+ `--fix`)
- [x] Create `src/spexl/cli/refs.py` with `register(subparsers)`:
  - `cmd_refs` – list reference specs
- [x] Update `prog="spectl"` → `prog="spexl"` in help text
- [x] Ensure `--dir` flag works as before (passed to `resolve_spec_root` from specroot.py)
- [x] Delete `src/spexl/cli/spectl.py` once port is verified

### 1.4 Template resolution module

- [x] Create `src/spexl/templates.py` with `read_template(category, name)` and `list_templates(category)`
- [x] Use `importlib.resources.files("spexl.templates")` for path resolution
- [x] Categories: `partials`, `actions`, `agents`, `concepts`, `artifacts`
- [x] Raise `FileNotFoundError` with helpful message if template doesn't exist
- [x] Add `__init__.py` files to template subdirectories if needed for `importlib.resources`

### 1.5 Test migration

- [x] Update all test imports to new module paths (`spexl.cli.changes`, `spexl.cli.validate`, `spexl.specroot`, etc.)
- [x] Update test fixtures that reference `SpectlError` → `SpexlError`
- [x] Update any subprocess calls from `python3 scripts/spectl.py` → direct function calls
- [x] Verify all 11 existing test files pass: `uv run pytest`

## 2. Decompose skill-core.md into partials

- [x] Create `partials/rules.md`: extract lines 46-57 from skill-core.md (5 rules + don'ts list)
- [x] Create `partials/structure.md`: extract lines 93-119 (directory layout diagram, delta targeting, monorepo note)
- [x] Create `partials/file-ownership.md`: extract lines 33-43 (ownership table + "changing spec invalidates design" warning)
- [x] Create `partials/cross-phase.md`: extract lines 132-139 (iteration, apply snags, scope changes)
- [x] Create `partials/interactive-vs-autonomous.md`: extract lines 121-131 (mode differences, when to pause)
- [x] Verify `partials/critique.md` already covers lines 141-156; supplement if needed (critique modes table, verdicts, escalation)
- [x] Delete `partials/skill-core.md`
- [x] Verify: `list_templates("partials")` returns all expected partial names

## 3. Adapt action templates for standalone use

Current `templates/actions/*.md` files have relative path references that assume they're loaded alongside SKILL.md. Each needs updating:

- [x] `actions/propose.md`: replace "read [references/spec.md]" → "run `spexl context spec-notation`"; replace "use `templates/proposal.md`" → "run `spexl template proposal`"; replace "python3 scripts/spectl.py" → "spexl"
- [x] `actions/apply.md`: same pattern – replace template/reference paths with `spexl context` and `spexl template` calls
- [x] `actions/explore.md`: lighter changes (explore has fewer artifact references)
- [x] `actions/archive.md`: replace spec-sync agent reference path, replace spectl calls
- [x] Create `actions/refine.md` – currently refine is only in SKILL.md's routing table (lines 82-91). Extract the routing logic + artifact reference pattern into a standalone action file.

## 4. Runtime steering commands

### 4.1 Context command

- [x] Create `src/spexl/cli/steering.py` with `register(subparsers)`
- [x] Implement `cmd_context(args)` that reads and composes content based on topic
- [x] Topic registry mapping topic names to template sources:

```
propose     → partials/rules + partials/cross-phase + actions/propose
apply       → partials/rules + partials/cross-phase + partials/interactive-vs-autonomous + actions/apply
explore     → partials/rules + actions/explore
refine      → partials/rules + partials/file-ownership + actions/refine
archive     → partials/rules + actions/archive
rules       → partials/rules
structure   → partials/structure
cross-phase → partials/cross-phase
concepts    → concepts/concepts
critique    → partials/critique
spec-notation → partials/spec (the artifact-writing guidance for spec deltas)
```

- [x] `--list` flag prints topic names with one-line descriptions, exits 0
- [x] Unknown topic → print error listing valid topics, exit 1
- [x] Output goes to stdout (agent captures via Bash tool)

### 4.2 Template command

- [x] Implement `cmd_template(args)` that prints an artifact template to stdout
- [x] Artifact type registry: `proposal`, `spec-delta`, `reference-spec`, `design`, `tasks`, `notes`
- [x] `--list` flag prints available type names, exits 0
- [x] Unknown type → print error listing valid types, exit 1

## 5. Skill generation

### 5.1 Composition engine

- [x] Create `src/spexl/generate/compose.py`
- [x] `compose_skill(action_name: str) -> str` assembles a complete SKILL.md from the manifest
- [x] Define `SKILL_MANIFESTS` dict mapping action names to `{description, partials, action}`
- [x] Description for each skill uses third-person trigger phrases per skill-development best practices
- [x] Output format: metadata comment → YAML frontmatter → `# Action Name` → partials (each with `<!-- spexl:section -->` marker) → action content → steering reference section
- [x] Include spexl version (from `importlib.metadata`) and generation date in metadata comment

### 5.2 Init command

- [x] Create `src/spexl/cli/generate.py` with `register(subparsers)`
- [x] `cmd_init(args)` accepts `target` positional arg (only `claude` supported initially)
- [x] Detects existing spexl-generated skills by checking for `<!-- Generated by spexl` in `.claude/skills/spexl-*/SKILL.md`
- [x] If skills exist → print warning, suggest `spexl update`, exit 1
- [x] Creates `.claude/skills/spexl-<action>/SKILL.md` for each action
- [x] Copies agent templates to `.claude/agents/`
- [x] Creates `specs/reference/` and `specs/changes/` if missing
- [x] Prints summary: N skills generated, N agents copied, specs dir status

### 5.3 Update command

- [x] `cmd_update(args)` finds existing spexl-generated skills
- [x] If none found → print error, suggest `spexl init claude`, exit 1
- [x] Compare version in metadata comment vs current spexl version
- [x] If same → print "Already up to date", exit 0
- [x] If different → regenerate each skill, print per-file diff summary (files changed / unchanged)
- [x] Also re-copy agent templates (they may have updated)

## 6. Verification

### 6.1 Unit tests

- [x] Tests for `templates.py`: `read_template` returns content, `list_templates` returns expected names, missing template raises error
- [x] Tests for `cmd_context`: each topic produces output, unknown topic exits 1, `--list` works
- [x] Tests for `cmd_template`: each artifact type produces output, unknown type exits 1, `--list` works
- [x] Tests for `compose_skill`: output contains frontmatter, contains rules, contains action content, contains steering section

### 6.2 Integration tests

- [x] `spexl init claude` in a temp dir creates expected file tree
- [x] `spexl init claude` twice → exit 1 with suggestion
- [x] `spexl update` after init → "Already up to date"
- [x] `spexl update` after version bump → regenerates, prints diff
- [x] `spexl update` without init → exit 1 with suggestion
- [x] Generated skill content: grep for `spexl context`, `spexl template`, `spexl new` to confirm steering references

### 6.3 Regression

- [x] All existing tests pass under new module structure (changes, links, validate, refs, etc.)
- [x] `spexl new`, `spexl changes`, `spexl validate`, `spexl archive`, `spexl info`, `spexl refs`, `spexl link`, `spexl unlink` – all behave identically to spectl

## Notes

**Dependency graph:**
- Phase 1 (foundation) and phase 2 (decompose partials) can proceed in parallel
- Phase 3 (adapt actions) depends on phase 2 being done (to know the final partial names for `spexl context` references)
- Phase 4 (steering) depends on phases 1 (templates.py) and 2 (partials exist)
- Phase 5 (generation) depends on phases 2, 3, and 4 (needs partials, adapted actions, and steering to reference)
- Phase 6 (verification) runs incrementally alongside each phase

**Recommended implementation order:** 1.1 → 1.2 → 1.3 → 1.5 (verify all commands work) → 1.4 → 2 → 3 → 4 → 5 → 6
