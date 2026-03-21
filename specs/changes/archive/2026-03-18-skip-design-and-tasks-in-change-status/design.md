## Context

`compute_status` in `specroot.py` checks for four artifacts (proposal, design, tasks, deltas) and returns "drafting" if any are missing. Small changes that don't need design or tasks get stuck in "drafting" unless you create empty placeholder files. `.change.json` already stores per-change metadata (`id`, `created`, `links`, `archived`).

## Goals / Non-Goals

**Goals:**
- Let `compute_status` skip design/tasks checks when explicitly marked in `.change.json`
- Expose `--skip` on `spexl new` for ergonomic creation
- Validate skip values in `spexl validate`

**Non-Goals:**
- Auto-inferring whether design/tasks should be skipped (always explicit)
- Skipping proposal or deltas (those are always required)

## Decisions

### Skip field shape in `.change.json`

```json
{
  "id": "xl16z",
  "created": "2026-03-18",
  "skip": ["design", "tasks"]
}
```

A list of strings. Only `"design"` and `"tasks"` are valid values. The field is omitted entirely when empty (no `"skip": []`).

**Alternatives considered:** A `"size": "small"` enum that implies skipping – rejected because it's indirect and couples skip logic to an opinionated size classification.

### Status when tasks are skipped

When `tasks` is in the skip list, there's no checklist to evaluate. The status transitions become:

| proposal | design (or skipped) | deltas | tasks (or skipped) | status |
|----------|-------------------|--------|-------------------|--------|
| missing | any | any | any | drafting |
| present | missing | any | any | drafting |
| present | present/skipped | missing | any | drafting |
| present | present/skipped | present | missing | drafting |
| present | present/skipped | present | skipped | complete |
| present | present/skipped | present | present (0 checked) | ready |
| present | present/skipped | present | present (partial) | in progress |
| present | present/skipped | present | present (all checked) | complete |

When tasks are skipped, there's no intermediate "ready" or "in progress" state – proposal + deltas is all there is, so the change is immediately complete.

### `compute_status` reads `.change.json` itself

`compute_status` currently takes only `change_path`. It will now also read `.change.json` to get the skip list. No signature change needed – the path gives access to the file.

### `--skip` flag on `spexl new`

Repeatable flag: `--skip design --skip tasks`. Writes the list to `.change.json` at creation. Uses `action="append"` with `default=None` so the field is omitted when not provided.

### Validation of skip values

`validate_change` checks that `skip` (if present) is a list containing only `"design"` and/or `"tasks"`. Invalid values (e.g. `"proposal"`, `"deltas"`) produce an error. Not auto-fixable.

## Risks / Trade-offs / Limitations

[Risk: changes stuck at "complete" without verification] → The user can skip tasks on a change that genuinely needs a checklist. Mitigation: this is an explicit opt-in, not a default. The `archive` command's task-completion guard still applies to whatever tasks exist.
