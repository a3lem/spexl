## Context

The `/archive` flow currently has the main agent merge delta specs into reference specs inline. This is mechanical work -- parsing markdown structure, matching requirements by heading, interleaving content -- that needlessly occupies the main agent's context window. Delegating to a subagent keeps the main agent focused on orchestration.

The spec-critic agent already demonstrates the subagent pattern: a focused agent definition (`agents/spec-critic.md`) with frontmatter, invoked via the Agent tool. The deliverable is a prompt file, not application code.

## Goals / Non-Goals

**Goals:**
- Agent definition at `agents/spec-sync.md` that handles all delta-to-reference merging
- Clean integration into the `/archive` flow via `references/archive.md`
- Correct handling of all four operators (ADDED, MODIFIED, REMOVED, RENAMED)
- Graceful error handling with AskUserQuestion for ambiguous cases

**Non-Goals:**
- Automated testing of the agent (subagents are validated by spec-critic post-merge)
- Programmatic markdown parsing (the agent uses LLM comprehension, not regex)
- Changes to spectl (it already prints the sync summary; merging was never its job)

## Decisions

### Agent definition follows spec-critic pattern

Frontmatter with `name`, `description`, `model`, `allowed-tools`, `skills`. Body contains invocation contract, process steps, and examples.

**Model:** `sonnet` -- the merge task is structured and mechanical, doesn't need opus-level reasoning. Matches spec-critic.

**Allowed tools:** `Read`, `Edit`, `Write`, `Glob`. Needs Read to inspect deltas and reference specs, Edit for modifying existing reference specs, Write for creating new capability specs, Glob for discovering `deltas/*/spec.md` files and checking whether reference specs exist.

**Skills:** `spec-driven-development` -- so it can access templates and understand spec structure.

### Merge algorithm is prompt-driven, not programmatic

The agent reads each delta spec, identifies operator sections (## ADDED/MODIFIED/REMOVED/RENAMED), and applies them to the reference spec using its understanding of markdown structure. No regex parsing, no AST -- just careful reading and editing.

This works because:
- Delta specs follow a known template (`change-spec.md`)
- Reference specs follow a known template (`reference-spec.md`)
- The hierarchy is fixed: OPERATOR > REQUIREMENT > SCENARIO
- The agent can use Edit for surgical changes and Write only for new files

**Alternatives considered:** A Python script that parses markdown headings mechanically. Rejected because markdown structure varies enough that an LLM handles edge cases better than rigid parsing, and the volume is small (typically 1-5 deltas per change).

### Processing order: one delta at a time

The agent processes deltas sequentially, one capability at a time. For each delta:

1. Read `deltas/<capability>/spec.md`
2. Check if `specs/reference/<capability>/spec.md` exists (Glob)
3. If exists: apply operators via Edit (MODIFIED, REMOVED, RENAMED) then append ADDED
4. If new: Write new file using `templates/reference-spec.md` as base, populate with ADDED requirements

Within a delta, operators are applied in order: REMOVED first (delete blocks), then RENAMED (update headings), then MODIFIED (replace blocks), then ADDED (append). This ordering prevents conflicts -- you don't want to add something then immediately try to modify it, or rename something after it's been removed.

### Invocation contract

The main agent invokes spec-sync with a prompt like:

```
Merge the delta specs from [change-dir] into the reference specs.
Spec root: [spec-root]
```

The agent discovers everything else by reading the filesystem. It does not receive pre-parsed data.

### Integration point in archive flow

The `/archive` flow (documented in `references/archive.md`) changes from:

```
1. Check completeness
2. Show sync summary (spectl archive --dry-run)
3. Merge deltas into reference specs  ← main agent does this inline
4. Validate merged specs (spec-critic)
5. Move to archive (spectl archive)
```

To:

```
1. Check completeness
2. Show sync summary (spectl archive --dry-run)
3. Invoke spec-sync agent  ← delegated to subagent
4. Validate merged specs (spec-critic)
5. Move to archive (spectl archive)
```

`references/archive.md` step 3 will reference the spec-sync agent instead of inline merge instructions. The rest of the flow stays the same.

### Error recovery uses AskUserQuestion

Per the spec's error handling requirement:
- MODIFIED targeting a missing requirement → silently treat as ADDED (reasonable assumption: the requirement is new under a different name or was never in reference)
- REMOVED targeting a missing requirement → skip silently (already gone)
- RENAMED targeting a missing requirement → AskUserQuestion (ambiguous -- user needs to decide)
- Malformed delta → AskUserQuestion (can't proceed without guidance)

The agent should not silently swallow errors that indicate a real problem. The threshold: if the operation can be interpreted unambiguously, handle it; if not, ask.

## Risks / Trade-offs

LLM-driven merge may produce inconsistent formatting across runs → Mitigated by using Edit (preserves surrounding content) and by spec-critic validation post-merge.

Sonnet may struggle with large reference specs (many requirements) → Mitigated by the fact that most reference specs are small. If this becomes a problem, the agent can be upgraded to opus for specific invocations.

## Open Questions

None.
