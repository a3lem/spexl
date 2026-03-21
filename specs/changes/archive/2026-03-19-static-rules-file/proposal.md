## Why

`spexl prime` outputs foundational knowledge formatted for system prompt injection. Currently there's no mechanism to get this into the agent's context automatically. The rejected `add-hooks-on-init` change proposed a SessionStart hook, but a static rules file is simpler: the prime content only changes when spexl itself is updated, so a file refreshed by `spexl update` is equally correct with fewer moving parts.

## What Changes

- **`spexl init claude` generates a rules file** – writes the output of `spexl prime` to `.claude/rules/spexl.md` alongside skills and agents. Claude Code auto-loads rules files, so no hook is needed.
- **`spexl update` regenerates the rules file** – refreshes `.claude/rules/spexl.md` when spexl's version changes, same as it already does for skills and agents.

## Capabilities

### Modified Capabilities

- `skill-generation`: `init` and `update` gain rules file generation; skill composition drops foundational content (now covered by the rules file)
- `knowledge-priming`: documents that `prime` output is persisted as a static rules file by `init`/`update`

## Impact

- `src/spexl/cli/generate.py` – write `.claude/rules/spexl.md` during init and update
- `src/spexl/generate/compose.py` – skill composition can exclude foundational methodology (covered by rules file)
- Tests – init/update tests verify rules file generation
