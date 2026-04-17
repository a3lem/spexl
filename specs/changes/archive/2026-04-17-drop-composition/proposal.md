## Why

spexl generated agent skills by composing partials, actions, and steering footers at install time. This indirection made it hard to reason about what the agent actually sees. Methodology content was duplicated across three surfaces (prime, skills, explain), creating contradiction risk. When critical information was missed during dogfooding, it was unclear whether the cause was a partial not being wired, content lost in composition, or an explain topic the agent never called.

The fix: stop composing. Hand-write each skill file. Serve shared methodology via a single librarian skill that action skills explicitly invoke first. Collapse prime/explain/template into a single `onboard` command that prints a primer for manual paste into AGENTS.md/CLAUDE.md.

Single source of truth for methodology content: the librarian skill's `references/` directory. No composition, no partials, no contradiction risk.

## What Changes

- **BREAKING**: `spexl prime` renamed to `spexl onboard`. Output changed: primer goes to stdout for clean piping; "paste into AGENTS.md" header goes to stderr.
- **BREAKING**: `spexl explain` removed. Knowledge is served by reading the librarian skill's `references/` files (or the files directly on disk after install).
- **BREAKING**: `spexl template` removed. Artifact templates are no longer served via CLI. Agents write proposals/specs from the guidance embedded in action skill SKILL.md files.
- **BREAKING**: `spexl init` no longer writes `.claude/rules/spexl.md`. The onboard primer is now pasted manually into AGENTS.md/CLAUDE.md by the user. Legacy `rules/spexl.md` files are auto-removed on refresh.
- **BREAKING**: Skill files are no longer composed from partials. Each skill is hand-written at `src/spexl/content/skills/<name>/SKILL.md`. A new librarian skill, `learn-about-sdd-with-spexl`, holds the shared methodology as `references/*.md`.
- **BREAKING**: Generated SKILL.md files no longer carry `metadata:` frontmatter (no `generated_by`, no `generated_on`). Skills are installed verbatim.
- **BREAKING**: Every action skill now opens with "invoke `learn-about-sdd-with-spexl` first" and names which reference files to load. Action skills no longer reference `spexl explain`, `spexl context`, or `spexl template`.
- Source content relocated from `src/spexl/templates/` (partials, actions, concepts, prime, artifacts) to `src/spexl/content/` (skills, agents, onboard.md).
- `src/spexl/generate/compose.py` deleted.
- `spexl init` now walks the content tree and copies files verbatim, preserving the directory layout under `.claude/skills/<skill>/` and `.claude/agents/`.

## Capabilities

### New Capabilities

- `onboarding`: A single command that prints a short primer suitable for manual paste into AGENTS.md or CLAUDE.md.

### Modified Capabilities

- `cli`: Package structure no longer contains `templates/partials/`, `templates/actions/`, `templates/concepts/`, `templates/prime/`, `templates/artifacts/`, or `generate/compose.py`. Template resolution no longer applies; content is served from `spexl.content` via `importlib.resources`.
- `skill-generation`: Init no longer composes skills or writes a rules file. It copies the `spexl.content` tree verbatim. The librarian skill (`learn-about-sdd-with-spexl`) is installed alongside the five action skills. Generated files carry no metadata frontmatter.

### Removed Capabilities

- `knowledge-priming`: Replaced by `onboarding`. The `prime` command and its `.claude/rules/spexl.md` output are gone.
- `runtime-steering`: Removed entirely. The `explain` and `template` commands are gone. Agents load methodology from the librarian skill's reference files.

## Impact

- Contributors editing methodology content now edit one file in `src/spexl/content/skills/learn-about-sdd-with-spexl/references/`. No mirrored edits across partials, prime, and concepts.
- Action skill authors write the SKILL.md by hand. No templating engine, no manifest.
- Downstream projects that ran `spexl prime` in a hook need to switch to `spexl onboard` (or manual paste). There is no migration script; the rename is breaking by design to surface the behavior change.
- Downstream projects that relied on `spexl explain` or `spexl template` in their skills or scripts must read the librarian's reference files directly or drop the CLI dependency.
