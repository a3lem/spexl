---
name: project_skill_token_budget
description: Resolved decision on knowledge delivery - three-level architecture with prime (hook), skills (self-contained), and explain (on-demand CLI)
type: project
---

The skill-vs-runtime-steering question is resolved. Three levels of knowledge delivery:

1. **Level 1 (foundational):** `spexl prime` injected via SessionStart hook. Shared methodology, loaded once per session.
2. **Level 2 (operational):** Baked into each skill. Self-contained for the phase, including templates. No extra tool calls needed.
3. **Level 3 (advanced/niche):** `spexl explain <topic>` called on demand by the model when it needs deeper guidance.

**Why:** Eliminates duplication across skills, avoids the `--already-covered` complexity, and matches each knowledge level to the right delivery mechanism.

**How to apply:** When generating skills, include operational instructions and templates inline. Don't duplicate Level 1 content in skills. Level 3 topics are pull-only.
