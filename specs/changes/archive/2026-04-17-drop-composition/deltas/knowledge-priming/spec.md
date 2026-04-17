# Knowledge Priming

## REMOVED Requirements

### Requirement: Prime command
**Reason**: The `prime` command is replaced by `onboard` in a new `onboarding` capability. The old behavior assumed prime output would be piped through a SessionStart hook into the agent's context on every session, and was also written to `.claude/rules/spexl.md` by `spexl init`. Both mechanisms are gone: `spexl init` no longer writes a rules file, and the primer is now meant for manual paste into AGENTS.md/CLAUDE.md once, not runtime injection per session.

**Migration**:
- Rename calls from `spexl prime` to `spexl onboard`.
- If `spexl prime` was wired into a SessionStart hook, remove the hook and instead pipe `spexl onboard >> AGENTS.md` (or `>> CLAUDE.md`) once to establish the always-on context. The header instruction is printed to stderr, so redirection writes only the primer content.
- Any automation that relied on `.claude/rules/spexl.md` being written by `spexl init` must be updated. `spexl init` no longer writes that file; `spexl init` refresh removes it if present.

*(This capability has no remaining requirements after the removal and SHALL be deleted from `specs/reference/` on archive.)*
