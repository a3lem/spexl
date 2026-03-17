## Why

The spec-driven development tool currently lives as a Claude Code plugin (`spec-driven-dev`) inside a marketplace repo. The skill architecture doesn't work: when users invoke `/propose`, the command file loads but the actual SKILL.md with rules, templates, and references never reaches the agent. Claude improvises instead of following the methodology. Separately, the tool is locked to Claude Code – the methodology itself is agent-agnostic.

Rewriting as `spexl`, a standalone Python CLI installed via `uv tool install spexl`, solves both problems. The CLI owns the methodology (plumbing, validation, knowledge). Agent integrations become a generation target: `spexl init claude` produces self-contained skills that call back into spexl at runtime for context and templates. The skills stay lean; spexl serves knowledge on demand.

## What Changes

- Rename `spectl` → `spexl` with proper Python package structure (`src/spexl/`)
- Add **skill generation** system: `spexl init claude` and `spexl update` compose partials + action templates into self-contained SKILL.md files
- Add **runtime steering** commands: `spexl context <topic>` and `spexl template <artifact>` serve knowledge to generated skills during execution
- Restructure the template/knowledge corpus into `templates/{partials,actions,agents,concepts,artifacts}`
- Existing plumbing commands (`new`, `changes`, `validate`, `archive`, `info`, `refs`, `link`, `unlink`) carry over with the new name
- Drop the `commands/` directory from the plugin; skills replace commands entirely

## Capabilities

### New Capabilities

- `skill-generation`: Composing partials, action templates, agent definitions, and artifact templates into self-contained SKILL.md files for target agents. Handles `init <target>` and `update`.
- `runtime-steering`: Serving knowledge fragments (concepts, rules, cross-phase context) and artifact templates to generated skills at execution time via `context` and `template` subcommands.

### Modified Capabilities

- `cli`: Restructure from single-file `spectl.py` into a proper `src/spexl/` package with modular subcommand routing. All existing commands carry over; new commands (`init`, `update`, `context`, `template`) are added.

## Impact

- **Users**: Install via `uv tool install spexl` instead of installing a Claude Code plugin from a marketplace. Run `spexl init claude` in their project to get skills.
- **Existing spectl users**: The CLI name changes. All existing commands remain with identical behavior.
- **Claude Code plugin**: No longer needed as the primary distribution mechanism. The plugin becomes one generation target among potentially many.
- **Test suite**: Tests must update from `spectl` invocations to `spexl` module imports. The single-file script becomes a package.
