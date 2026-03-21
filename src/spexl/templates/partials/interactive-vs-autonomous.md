## Interactive vs Autonomous

**Interactive** (default): Ask the user at each phase for input and confirmation (use AskUserQuestion tool).

**Autonomous** (when user requests it, e.g. "work on this until done"):

1. **Propose:** Draft all artifacts. Invoke **spec-critic** (`intra-spec` after proposal, `intra-spec` + `spec-code` after specs + design).
2. **Apply:** Implement and verify against all requirements and scenarios. Invoke **spec-critic** (`all`) before marking complete.
3. **Archive:** Invoke **spec-sync** → validate with **spec-critic** (`inter-spec`) → move to archive.

Only pause for genuine ambiguities or when the critic can't resolve after 5 rounds.
