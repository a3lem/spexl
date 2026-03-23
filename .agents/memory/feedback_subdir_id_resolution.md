---
name: Sub-project change ID resolution
description: Commands that take a change ID must resolve it across all sub-project spec roots, not just the nearest one
type: feedback
---

Changes in subdirectories can be referenced by ID from any valid ancestor directory. This applies to all commands that accept a change identifier: `info`, `archive`, `link`, `unlink`.

**Why:** spexl supports multi-root projects (nested `.spexl.toml` files). A user running from the top-level project expects to reach any change beneath them by ID, regardless of which sub-project owns it.

**How to apply:** When implementing or modifying commands that resolve a change by identifier, use `discover_all_configs` (walk-down) rather than `discover_single_config` (walk-up to nearest). Iterate through all discovered configs trying `resolve_change` on each. All four commands (`info`, `archive`, `link`, `unlink`) now follow this pattern via `_resolve_across_configs` (changes.py) and `_resolve_change_identifier` (links.py). Any new command that accepts a change identifier must do the same.
