# Runtime Steering

## REMOVED Requirements

### Requirement: Template command
**Reason**: Artifact templates are no longer served via a CLI command. Action skills embed the necessary artifact structure directly in their SKILL.md (e.g., `spexl-propose/SKILL.md` describes the four required proposal sections and the delta section types inline). Agents write artifacts from that guidance, not from a separately-fetched template.

**Migration**: Replace any `spexl template <type>` invocation with the guidance embedded in the relevant action skill. For proposal structure, see `spexl-propose/SKILL.md`. For delta structure, see the librarian's `references/spec-notation.md`.

### Requirement: Explain command
**Reason**: Methodology knowledge is served by the `learn-about-sdd-with-spexl` skill, which action skills explicitly invoke and then read the relevant `references/*.md` file. CLI-based on-demand knowledge delivery is redundant: the skill loading mechanism is the native way to deliver progressive knowledge in the agent's context, and it avoids the three-surface contradiction risk that motivated this change.

**Migration**: Replace any `spexl explain <topic>` invocation with a direct read of the librarian's reference file:
- `spexl explain spec-notation` → read `learn-about-sdd-with-spexl/references/spec-notation.md`
- `spexl explain verification` → read `learn-about-sdd-with-spexl/references/verification.md`
- `spexl explain critique` → read `learn-about-sdd-with-spexl/references/critique.md`
- `spexl explain design` → read `learn-about-sdd-with-spexl/references/design-guidance.md`
- `spexl explain tasks` → read `learn-about-sdd-with-spexl/references/tasks-guidance.md`
- `spexl explain spexl` → read `learn-about-sdd-with-spexl/references/concepts.md`

*(This capability has no remaining requirements after the removal and SHALL be deleted from `specs/reference/` on archive.)*
