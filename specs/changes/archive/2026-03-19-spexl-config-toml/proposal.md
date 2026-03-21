## Why

Currently `spexl update` would need to sniff the filesystem to figure out which target (e.g. claude) was used during `init`. A project-level config file gives spexl a persistent place to store this and other project-scoped settings – active target, enabled agents, custom explain topics, etc.

Parked for now. Flesh out after `add-hooks-on-init` lands and the need for stored config becomes concrete.

## What Changes

- **Project config file** – `spexl.toml` (location TBD: project root, `specs/`, or `.config/`) stores project-level spexl settings.
- **`init` writes config** – `spexl init claude` writes the target to config so `update` can read it back.
- **`update` reads config** – no need to pass the target again.

## Capabilities

### New Capabilities

- `project-config`: Reading/writing `spexl.toml` for project-scoped settings

### Modified Capabilities

- `skill-generation`: `init` writes config, `update` reads it

## Impact

[CLARIFICATION NEEDED] – scope depends on what settings end up living here. Keeping this minimal until the need crystallizes.
