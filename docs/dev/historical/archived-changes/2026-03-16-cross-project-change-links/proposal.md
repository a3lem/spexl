## Why

In a monorepo, a change to a service often requires a corresponding change to a library it depends on. Today there's no way to express that two changes in different `specs/` directories are related. Each change is self-contained, which is correct for single-project work but leaves a gap for cross-project coordination: you can archive one side of a linked pair without noticing the other, or miss that a change in `services/api/` has a companion in `libs/auth/`.

The fix is a lightweight linking mechanism in `.change.json` -- not a new layer, not top-level specs, just a `links` field that points from one change to another across spec roots. `spectl` can then warn on archive, validate link integrity, and surface related changes in `info` output.

## What Changes

- `.change.json` gains an optional `links` field: an array of `{"specs": "<relative-path-to-other-specs-dir>", "change": "<change-id>"}` entries
- New `spectl link` command creates bidirectional links between two changes
- New `spectl unlink` command removes a link from both sides
- `spectl info` shows linked changes and their status
- `spectl archive` warns if linked changes are still active
- `spectl validate` checks that linked specs directories exist and change IDs resolve

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `spectl`: Adds `link` and `unlink` commands, extends `info`/`archive`/`validate` to handle links

## Impact

- `scripts/spectl.py` -- new commands and validation logic
- `.change.json` schema -- new optional `links` field
- `docs/concepts.md` -- should document cross-project linking
- `skills/spec-driven-development/SKILL.md` -- monorepo section should mention linking
- `skills/spec-driven-development/references/critique.md` -- `inter-spec` mode should follow links
