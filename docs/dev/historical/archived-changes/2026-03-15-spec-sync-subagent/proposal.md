## Why

The archive phase requires merging delta specs into reference specs -- applying ADDED, MODIFIED, REMOVED, and RENAMED sections to existing markdown files. This is not a mechanical string operation; it requires understanding markdown structure, placing requirements in the right sections, and handling edge cases (new capabilities, partial overlaps, section ordering). The main agent currently does this inline during `/archive`, which is error-prone and hard to validate.

A dedicated subagent (like spec-critic) can focus entirely on the merge, be invoked by the main agent, and be validated by the spec-critic afterward.

## What Changes

- New `spec-sync` subagent that handles delta-to-reference merging
- The `/archive` flow delegates sync to this agent instead of doing it inline
- spec-critic validates the result after sync completes

## Capabilities

### New Capabilities
- `spec-sync`: Subagent that merges delta specs into reference specs

## Impact

- New `agents/spec-sync.md` agent definition
- `references/archive.md` updated to delegate merge to spec-sync agent
- `SKILL.md` sub-agents table updated
