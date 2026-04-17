# Interactive vs Autonomous

**Interactive** (default): Ask the user at each phase for input and confirmation. Use AskUserQuestion for decision points. Surface ambiguities rather than guessing.

**Autonomous** (when user requests it, e.g. "work on this until done"):

1. **Propose:** Draft all artifacts. Invoke **spexl-spec-critic** (`intra-spec` after proposal, `intra-spec` + `spec-code` after specs + design).
2. **Apply:** Implement and verify against all requirements and scenarios. Invoke **spexl-spec-critic** (`all`) before marking complete.
3. **Archive:** Invoke **spexl-spec-sync** → validate with **spexl-spec-critic** (`inter-spec`) → move to archive.
4. **Refine** (in autonomous mode): Document the refinement in `notes/` and proceed.

Only pause for genuine ambiguities or when the critic can't resolve after 5 rounds.

## Iteration Across Phases

All phases can be revisited.

- Apply snag → may reveal a design flaw, spec gap, or proposal issue
- Changing a spec may invalidate the design -- always warn the user
- Scope changes require user confirmation in interactive mode; in autonomous mode, document in `notes/` and proceed
