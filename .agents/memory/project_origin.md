---
name: project_origin
description: How spexl originated from the spec-driven-dev Claude Code plugin and the loading problem that motivated the rewrite
type: project
---

spexl is a rewrite of the `spec-driven-dev` Claude Code plugin (from `my-claude-plugins` marketplace repo). The plugin's skill architecture failed: when users invoked `/propose` in external projects, the command file loaded but SKILL.md (with all rules, templates, references) never reached the agent. Claude improvised instead of following the methodology.

**Why:** See `docs/HISTORY.md` for the full narrative. The core decision was to make spexl a standalone CLI (`uv tool install spexl`) that owns the methodology, with agent integrations as a generation target rather than the primary distribution.

**How to apply:** The old plugin still exists at `~/Code/projects/my-claude-plugins/plugins/spec-driven-dev/` for reference. Historical archived changes from the plugin era are in `docs/historical/`.
