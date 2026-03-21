## Why

`spexl init claude` currently generates skills and agents non-interactively. It doesn't install the SessionStart hook needed for the three-level knowledge architecture (where `spexl prime` injects foundational knowledge at session start). It also doesn't guide the user through setup decisions like where to install.

This change makes `init` an interactive, human-facing command that sets up everything needed for spexl in a Claude Code project: skills, agents, and the SessionStart hook that runs `spexl prime`.

## What Changes

- **Interactive prompts** – `spexl init claude` asks the user where to install (current dir or search up for nearest `.claude/` / `CLAUDE.md`), shows what will be installed, and confirms before proceeding. If no `.claude/` is found, prompts to create one.
- **SessionStart hook** – writes a hook entry to `.claude/settings.local.json` that runs `spexl prime` on session start.
- **Skills include templates inline** – generated skills for frequently used phases (propose, apply) bake artifact templates directly into the skill body.
- **`update` detects target** – `spexl update` detects the installed target from existing config and refreshes skills, agents, and hook.
- **`specs/` scaffolding** – creates `specs/reference/` and `specs/changes/` if missing.

## Capabilities

### Modified Capabilities

- `skill-generation`: `init` becomes interactive with hook setup and `.claude/` discovery; `update` auto-detects target; skills restructured for three-level knowledge architecture

## Impact

- `src/spexl/cli/generate.py` – interactive prompts, hook installation logic, `.claude/` discovery
- `src/spexl/generate/compose.py` – skill composition updated to include templates inline, exclude Level 1 content
- `.claude/settings.local.json` – new SessionStart hook entry added during init
- Tests – init tests need to account for interactive prompts and hook setup
