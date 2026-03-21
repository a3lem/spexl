## Why

Computed status requires all four artifacts (proposal, design, tasks, deltas) before a change can leave "drafting." This is too rigid for small changes where design or tasks add no value. The result is either skipping the status system entirely or creating empty placeholder files.

A `skip` field in `.change.json` lets the user explicitly mark design and/or tasks as not needed for a given change. The status computation treats skipped artifacts as present. The intent is recorded in metadata, not inferred.

## What Changes

- **`skip` field in `.change.json`** -- an optional list of artifact names (e.g. `["design", "tasks"]`) that the status computation treats as present.
- **`compute_status` updated** -- skipped artifacts don't block the transition out of "drafting."
- **`spexl new` gains `--skip` flag** -- `spexl new my-change --skip design --skip tasks` writes the skip list into `.change.json` at creation time.
- **`spexl validate` checks skip values** -- only `design` and `tasks` are valid skip targets. Invalid values produce a validation error.

## Capabilities

### Modified Capabilities

- `cli`: `compute_status` respects skip list; `new` command gains `--skip` flag; `validate` checks skip values

## Impact

- `src/spexl/specroot.py` -- `compute_status` reads skip list from `.change.json`
- `src/spexl/cli/changes.py` -- `new` command writes skip field
- `src/spexl/cli/validate.py` -- validates skip field values
- Tests -- new status tests with skip combinations
