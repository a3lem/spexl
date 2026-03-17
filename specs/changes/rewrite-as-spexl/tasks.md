## 1. Package foundation

- [ ] Decompose `cli/spectl.py` into `cli/plumbing.py` (extract functions, keep behavior identical)
- [ ] Create `templates.py` with `importlib.resources`-based template/partial resolution
- [ ] Wire up argparse in `__init__.py:main()` with subparsers for all subcommands
- [ ] Add `--version` flag reading from package metadata
- [ ] Verify `src/spexl/templates/` is included as package data (lives inside the package, so automatic with uv_build)
- [ ] Update all test imports from `spectl` to `spexl` module paths

## 2. Decompose skill-core.md into partials

- [ ] Extract `partials/rules.md` from skill-core.md (5 core rules + don'ts)
- [ ] Extract `partials/structure.md` (directory layout and conventions)
- [ ] Extract `partials/file-ownership.md` (ownership table + warnings)
- [ ] Extract `partials/cross-phase.md` (phase interaction implications)
- [ ] Extract `partials/interactive-vs-autonomous.md` (mode differences)
- [ ] Remove `partials/skill-core.md` once fully decomposed

## 3. Runtime steering commands

- [ ] Implement `spexl context <topic>` reading from partials and concepts
- [ ] Implement `spexl context --list` enumerating available topics
- [ ] Implement `spexl template <artifact-type>` printing artifact templates
- [ ] Implement `spexl template --list` enumerating available types
- [ ] Add topic-to-partial mapping (propose → rules + cross-phase + actions/propose.md)

## 4. Skill generation

- [ ] Implement `generate/compose.py` – assemble frontmatter + partials + action + steering references
- [ ] Implement `spexl init claude` – generate skills, agents, and specs directory
- [ ] Implement `spexl update` – detect existing generated files, regenerate, print diff summary
- [ ] Generate metadata comments with version and timestamp in each output file
- [ ] Adapt action templates (`templates/actions/*.md`) for standalone skill use (they currently assume SKILL.md is loaded)

## 5. Verification

- [ ] Tests for `spexl context` subcommand (all topics, unknown topic, --list)
- [ ] Tests for `spexl template` subcommand (all types, unknown type, --list)
- [ ] Tests for `spexl init claude` (fresh project, already initialized)
- [ ] Tests for `spexl update` (no drift, with changes, no prior init)
- [ ] Tests for generated skill content (contains rules, contains action instructions, is self-contained)
- [ ] Existing plumbing tests pass under new module structure
- [ ] End-to-end: `spexl init claude` → generated skill contains correct `spexl context` and `spexl template` references

## Notes

Phases 1-2 can proceed in parallel. Phase 3 depends on phase 2 (partials must exist). Phase 4 depends on phases 2 and 3. Phase 5 runs incrementally alongside each phase.
