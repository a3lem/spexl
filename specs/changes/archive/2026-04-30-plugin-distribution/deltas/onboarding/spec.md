# Onboarding

## REMOVED Requirements

### Requirement: Onboard command
**Reason**: The `spexl onboard` command printed a methodology primer for manual paste into AGENTS.md/CLAUDE.md. This content is now delivered via `AGENTS.md` and `CLAUDE.md` at the plugin root, loaded automatically by each agent's plugin system. No manual paste step is needed.
**Migration**: Users who previously ran `spexl onboard >> AGENTS.md` should remove the pasted block. The plugin delivers the same content via convention files (`AGENTS.md` for opencode/pi, `CLAUDE.md` for Claude Code). Running `spexl onboard` prints a friendly error pointing to the plugin mechanism.
