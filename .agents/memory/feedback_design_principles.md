---
name: feedback_design_principles
description: Two design principles - no deprecation concerns (pre-alpha) and self-contained skills with compositional CLI
type: feedback
---

1. **Pre-alpha, no deprecation concerns.** Don't worry about backwards compatibility or migration paths. Clean breaks are fine.

2. **Self-contained skills, compositional CLI.** Frequently used skills should be relatively self-contained (e.g. including templates directly in the skill body). But keep things compositional via CLI commands for other flows that may want to re-use information at a stage when the skill isn't loaded or doesn't need to be loaded.

**Why:** Skills are the hot path for AI agents – minimize tool calls. CLI commands serve the long tail of use cases (subagents, non-Claude workflows, humans).

**How to apply:** When deciding whether to bake content into a skill vs. expose via CLI: if it's needed every time the skill runs, bake it in. If it's needed occasionally or by other consumers, keep it as a CLI command too.
