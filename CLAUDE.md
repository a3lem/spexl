# CLAUDE.md

Spec-driven development CLI. Specs are the source of truth; code serves specs.

## What spexl Does

Three roles:
1. **Plumbing** – `new`, `changes`, `info`, `archive`, `validate`, `refs`, `link`, `unlink` (filesystem ops for spec management)
2. **Project setup** – `init` scaffolds `.spexl.toml` and `specs/`; `install <target>` installs agent skills/subagents/hooks
3. **Runtime steering** – `onboard` serves methodology knowledge on demand at runtime

## Project Structure

```
src/spexl/
├── __init__.py       # main() entry point, argparse routing
├── __main__.py       # `python -m spexl`
├── config.py         # .spexl.toml discovery/loading
├── errors.py         # SpexlError + exit-code conventions
├── specroot.py       # locate specs/ from CWD
├── cli/
│   ├── changes.py    # new, changes, info, archive
│   ├── install.py    # init (scaffold), install (agent assets)
│   ├── steering.py   # onboard (serves methodology content)
│   ├── refs.py       # refs
│   ├── links.py      # link, unlink
│   └── validate.py   # validate (+ --fix)
└── content/          # Package data shipped via importlib.resources
specs/                # spexl's own specs (dogfooding)
  ├── reference/      # Current reference specs
  └── changes/        # Active changes; archive/ holds completed ones
tests/                # pytest
.spexl.toml           # Project config (spec root, etc.)
```

## Running

- `uv run spexl` – run locally during development
- `uv run pytest` – run tests
- `uv tool install -e .` – install locally as a tool for end-to-end testing

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

