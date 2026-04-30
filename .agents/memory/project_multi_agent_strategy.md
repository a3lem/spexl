---
name: project_multi_agent_strategy
description: spexl targets multiple coding agents; install-command approach chosen over native plugins
type: project
---

Adriaan builds agent-oriented tools (spexl, epimem, tiquette) and wants a consistent distribution pattern across all of them. Primary target agents: Claude Code, opencode, pi.dev.

**Distribution model:** CLI install command (`<tool> install --target <agent>`) rather than native plugins per platform. Rationale documented in `docs/why-install-instead-of-plugins.md`. Key reasons: uniform UX, version-locked artifacts, per-target content rendering, covers agents without plugin systems.

**Content portability:** Skills follow the open Agent Skills standard (agentskills.io). Skill content should be written as agent-agnostic intent where possible ("ask the user for clarification") rather than agent-specific mechanism ("use AskUserQuestion tool"). Where agent-specific content is unavoidable, Jinja2 templates with per-target context handle the fork.

**Hook divergence:** Hooks vary structurally across agents. Claude Code uses shell commands + settings.json; opencode and pi.dev use JS/TS extensions with programmatic event APIs. The install command absorbs this divergence per target. For epimem (which needs dynamic content injection), hooks are required; for spexl (static methodology), skills and rules suffice.

**Reference projects studied:**
- OpenSpec (install-command approach, 28+ agents, thin per-tool adapters)
- superpowers (native plugins, shared skills, per-agent manifests)
- MiniMax skills (same pattern as superpowers)
- pi.dev docs (follows Agent Skills standard, reads .agents/ natively)

**How to apply:** When designing install behavior or content distribution, check this memory and `docs/why-install-instead-of-plugins.md`. Don't suggest native plugins without revisiting the tradeoffs already explored.
