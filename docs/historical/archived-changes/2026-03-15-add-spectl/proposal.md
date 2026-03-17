## Why

The SDD plugin's AI agent currently handles all spec management through file reads, writes, and directory operations. Creating a change requires reading references/propose.md, creating directories, writing `.change.json`, and creating `deltas/`. Archiving requires parsing delta sections, applying them to reference specs with Edit calls, and moving directories with date prefixes. These are mechanical operations where the AI adds no value and can introduce errors -- particularly the archive merge, which is the most error-prone part of the workflow.

A small CLI tool (`spectl`) would handle the mechanical parts, letting the AI focus on the parts that require judgment: gathering requirements, writing specs, designing solutions.

## What Changes

- New CLI tool `spectl` with commands: `new`, `changes`, `archived`, `info`, `archive`, `refs`, `validate`
- `.change.json` gains an `archived` field (with reason) when a change is archived
- `spectl archive` handles the mechanical parts (completeness check, sync summary, move to archive)

## Capabilities

### New Capabilities
- `spectl`: CLI tool for mechanical spec management (new, changes, archived, info, archive, refs, validate)

## Impact

- New binary/script in the repo (language TBD in design phase)
- `references/propose.md` can simplify its directory creation steps to "run `spectl new`"
- `references/archive.md` can simplify mechanical steps to "run `spectl archive`"
- `commands/*.md` may add `spectl` to allowed-tools
