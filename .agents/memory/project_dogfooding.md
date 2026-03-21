---
name: project_dogfooding
description: spexl dogfoods its own spec-driven methodology – always read the change specs before implementing
type: feedback
---

spexl uses its own spec-driven workflow on itself. The `specs/` directory contains change specs written in the same format that spexl manages.

Before implementing anything, read the active change spec: `specs/changes/rewrite-as-spexl/proposal.md` → `design.md` → `tasks.md` → `deltas/*/spec.md`. The specs are detailed and contain specific decisions about module structure, composition model, and implementation order.

**Why:** Adriaan designs thoroughly before implementing. Jumping to code without reading the specs will produce work that contradicts design decisions already made.

**How to apply:** When asked to implement, start by reading the relevant spec artifacts. Check task checkboxes for current progress. Follow the implementation order in `tasks.md`.
