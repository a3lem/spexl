# Backlog

Ideas and enhancements not yet promoted to a spec change.

## `spexl skip` command

`spexl skip <id-or-slug> <phase>...` to mark phases as skippable on an existing change. Writes to the `skip` field in `.change.json`.

Complement: `spexl unskip <id-or-slug> <phase>...` (or `spexl skip --undo`) to reverse it.

Replaces the current `spexl new --skip` workflow, which only works at creation time.
