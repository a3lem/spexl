---
id: spe-r0cz
status: open
deps: []
links: []
created: 2026-03-18T00:00:00Z
type: task
priority: 2
assignee: adriaan
tags: [prime, skills]
---
# Investigate overlap between prime.md and generated skill content

The prime instruction (injected into the system prompt) and the generated skills (composed from partials + actions) may duplicate content. Duplication risks contradictions creeping in when one side is updated but the other isn't.

Investigate: which content appears in both places? Can prime reference skills instead of repeating methodology details? Should partials be shared between prime composition and skill composition?
