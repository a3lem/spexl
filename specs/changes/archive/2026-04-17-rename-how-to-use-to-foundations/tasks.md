# Tasks

## Content tree

- [x] Rename `src/spexl/content/skills/spexl-how-to-use/` → `spexl-foundations/` (plain `mv`; directory was untracked in git)
- [x] Rewrite `src/spexl/content/skills/spexl-foundations/SKILL.md` concept-first: introduce software specifications, spec deltas, and spexl's dual methodology+CLI nature before the phase table; demote the reference index
- [x] Update every `spexl-how-to-use` mention in `src/spexl/content/skills/spexl-<action>/SKILL.md` (explore, propose, refine, apply, archive) to `spexl-foundations`
- [x] Update `skills:` frontmatter in `src/spexl/content/agents/spexl-spec-critic.md` and `src/spexl/content/agents/spexl-spec-sync.md`
- [x] Update `src/spexl/content/onboard.md` to point at `spexl-foundations`

## Code

- [x] Update `src/spexl/cli/steering.py` references to the methodology skill name

## Tests

- [x] Update path/name assertions in `tests/test_install.py`
- [x] Update assertions in `tests/test_steering.py`
- [x] `uv run pytest` passes (130 passing)

## Docs

- [x] `CHANGELOG.md`: add entry under Unreleased noting the rename (BREAKING: users must re-run `spexl install <target>`)
- [x] `TODO.md`: sole `how-to-use` mention is a historical log entry describing a previous rename; left as-is (not a current reference)

## Verification

- [x] Tests for skill-generation requirement: Install target -- `test_install.py::test_install_fresh_mirrors_source_tree` (and 11 other annotated tests) walk the source tree and assert the installed tree matches verbatim; with the source rename, this transitively verifies `spexl-foundations/` is installed and no `spexl-how-to-use/` remains
- [x] Tests for skill-generation requirement: Methodology skill -- `test_methodology_skill_references_install` checks the references/ subdirectory under the renamed skill path
- [x] Tests for skill-generation requirement: Agent generation -- `test_agents_declare_methodology_skill` asserts `skills: spexl-foundations` in agent frontmatter
- [x] Tests for onboarding requirement: Onboard command -- `test_onboard_prints_primer_to_stdout` asserts `spexl-foundations` is in the primer output; annotated with `# spec: onboarding requirement=onboard-command`
- [x] Tests for cli requirement: Package structure -- `test_discovery.py` tests cover the package-structure requirement; rename does not affect the cli capability's behavior, only the tree documented in the spec
- [x] End-to-end sanity: full suite runs via `uv run spexl install ...` under pytest against the in-tree content package; all paths resolve to `spexl-foundations`
- [x] Refresh sanity: covered by `test_install_idempotent_*`; the existing cleanup routine was not changed, so pre-existing coverage still applies

## Notes

- Spec deltas do not constrain the SKILL.md body prose; the concept-first rewrite is implementation. Guidance captured in the proposal's Impact section.
- No deprecation shim -- spexl is pre-1.0. Users re-install; refresh cleans up the stale directory.
- Added `# spec: onboarding ...` annotations to `test_steering.py` -- these tests existed but had no annotation; closing that small coverage gap as part of this change.
