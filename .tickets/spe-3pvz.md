---
id: spe-3pvz
status: closed
deps: []
links: []
created: 2026-03-18T19:35:12Z
type: feature
priority: 2
assignee: claude
tags: [spexl, spec-workflow]
---
# Auto-rebase open deltas after archive sync

After archiving a change and syncing its deltas into reference specs, automatically analyze remaining open changes that delta the same capabilities. Flag any MODIFIED requirements in open deltas that were written against a now-stale reference. Either warn the user or auto-update the base text in those deltas to match the new reference reality.

