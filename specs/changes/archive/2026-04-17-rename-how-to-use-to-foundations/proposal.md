# Proposal: Rename `spexl-how-to-use` to `spexl-foundations`

## Why

The skill serves two distinct jobs: introduce essential spec-driven-development concepts on first load (what a software specification is, what a spec delta is, that spexl is both a methodology and a CLI), and act as a reference base the action skills defer to for depth. The name `how-to-use` reads as operational ("how do I run the tool") and undersells the conceptual-introduction role. `foundations` signals both roles: the grounding a newcomer needs, and the canonical base the rest of the system refers back to.

## What Changes

- **BREAKING** Rename the methodology skill from `spexl-how-to-use` to `spexl-foundations`. This changes the installed path (`.claude/skills/spexl-foundations/`), the name used by action skills and agents when they defer to it, and the name mentioned in the onboard primer.
- Action skills (`spexl-explore`, `spexl-propose`, `spexl-refine`, `spexl-apply`, `spexl-archive`) instruct the agent to invoke `spexl-foundations` instead of `spexl-how-to-use`.
- Agent definitions (`spexl-spec-critic`, `spexl-spec-sync`) reference `spexl-foundations` in their frontmatter.
- The onboard primer (`spexl onboard`) names `spexl-foundations` as the methodology skill.
- Users who previously installed `spexl-how-to-use` via `spexl install <target>` need to re-run install; refresh removes the stale directory (existing cleanup behavior in `skill-generation` already handles this).
- No deprecation shim. Spexl is pre-1.0.

## Capabilities

### Modified Capabilities

- `skill-generation` -- every scenario that names `spexl-how-to-use` in an installed path, an agent frontmatter field, or the skill-defers-to-methodology rule is updated to name `spexl-foundations`.
- `onboarding` -- the primer's required content includes `spexl-foundations` in place of `spexl-how-to-use`.
- `cli` -- the package-structure tree in the `Package structure` requirement shows `spexl-foundations/` under `src/spexl/content/skills/`.

## Impact

**Source tree:**
- `src/spexl/content/skills/spexl-how-to-use/` -- rename to `spexl-foundations/`. `SKILL.md` and `references/` move with it.
- `src/spexl/content/skills/spexl-<action>/SKILL.md` (×5) -- every mention of `spexl-how-to-use` updates to `spexl-foundations`.
- `src/spexl/content/agents/spexl-spec-critic.md`, `spexl-spec-sync.md` -- `skills:` frontmatter updated.
- `src/spexl/content/onboard.md` -- primer text updated.

**Reference specs (this change's deltas):**
- `specs/reference/skill-generation/spec.md`
- `specs/reference/onboarding/spec.md`
- `specs/reference/cli/spec.md`

**Tests:**
- `tests/test_install.py`, `tests/test_steering.py` -- path/name assertions updated.

**Docs:**
- `CHANGELOG.md` -- new entry noting the rename.
- `TODO.md` -- mention updated.

**Out of scope for the spec deltas (but part of the apply phase):**
- The SKILL.md body will be rewritten concept-first (introducing specifications, deltas, and the methodology+CLI dual nature). The specs do not constrain the skill body's prose, so this rewrite is implementation, not a spec change. It is bundled into the same apply for atomicity.

**Migration:**
- Existing users re-run `spexl install <target>`. The refresh routine already removes files no longer in the content tree, so the stale `spexl-how-to-use/` directory is cleaned up automatically.
