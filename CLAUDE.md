# CLAUDE.md

Spec-driven development CLI. Specs are the source of truth; code serves specs.

## What spexl Does

Three roles:
1. **Plumbing** – `new`, `changes`, `validate`, `archive`, `info`, `refs`, `link`, `unlink` (filesystem ops for spec management)
2. **Skill generation** – `init claude`, `update` (compose partials + actions into self-contained SKILL.md files for AI agents)
3. **Runtime steering** – `context <topic>`, `template <artifact>` (serve knowledge on demand to generated skills during execution)

## Project Structure

```
src/spexl/
├── __init__.py          # main() entry point, argparse routing
├── cli/
│   ├── plumbing.py      # Existing spec management commands
│   ├── generate.py      # init, update
│   └── steering.py      # context, template
├── generate/
│   └── compose.py       # Skill composition (partials + actions → SKILL.md)
├── templates/           # Package data (importlib.resources)
│   ├── partials/        # Shared rule fragments composed into skills
│   ├── actions/         # Per-phase instructions (propose, apply, explore, refine, archive)
│   ├── agents/          # Agent definitions (spec-critic, spec-sync)
│   ├── concepts/        # Methodology docs (served by `spexl context`)
│   └── artifacts/       # Artifact templates (served by `spexl template`)
specs/                   # spexl's own specs (dogfooding)
docs/                    # Concepts, history, historical archived changes
tests/                   # pytest
```

## Running

- `uv run spexl` – run locally during development
- `uv run pytest` – run tests
- `uv tool install -e .` – install locally as a tool for end-to-end testing

## Active Change

`specs/changes/rewrite-as-spexl/` – the foundational change that restructures spectl into spexl. Three capability deltas: `cli`, `skill-generation`, `runtime-steering`. Read `proposal.md` first.

## CLI Design

spexl is intended for use by AI agents. All errors exit 1 with a clear explanation so the agent can reason about what went wrong. Prefer crashing over silent failures.

Whenever plumbing commands are updated, check whether `validate` (+ `--fix`) logic needs updating to cover new fields or invariants.

## Spec-Driven Workflow

```
explore [topic]       → Think before proposing
propose [description] → Create change + all artifacts (proposal, deltas, design, tasks)
refine [instruction]  → Update any artifact
apply [spec slug]     → Implement and verify
archive [spec slug]   → Sync deltas to reference + archive
```

## Inspiration

- [kiro](https://kiro.dev/docs/)
- [spec-kit](https://github.com/github/spec-kit)
- [openspec](https://github.com/nicobailon/openspec)
- [SDD tools (Fowler)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)


## Changelog and Versioning

## Changelog

Update CHANGELOG.md when committing notable changes.

Items should start with verbs like 'added', 'removed', 'fixed', 'improved', 'changed', etc.

## Versioning and release

1. Increment version number. Stick to 'zero-ver', as breaking changes are still possible.
2. Update CHANGELOG.md: change `## [Unreleased]` to version + date
3. Update `project.version=` in pyproject.toml.
4. Commit and tag:
   ```bash
   git add <relevant files>
   git commit -m "release: v0.4.0"
   git tag v0.4.0
   git push && git push origin v0.4.0
   ```

