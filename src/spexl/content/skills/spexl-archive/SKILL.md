---
name: spexl-archive
description: Archive a completed spexl change by merging its deltas into reference specs and moving the change to the archive directory. Use when the user asks to "archive", "merge deltas", "finalize", "complete a change", "wrap up", or references a change that has been applied and verified. Only archive when implementation is done and tests pass -- archiving a half-finished change leaves the reference specs inconsistent.
---

# Archive

Archive a completed change: merge its deltas into the reference specs, then move the change folder to `specs/changes/archive/`.

## Load Methodology First

Before doing anything else, invoke the `spexl-foundations` skill. Tell it you're in the **archive** phase and need the rules, directory structure (especially archive locations), and the `inter-spec` critic mode guidance.

## Process

### 1. Check completeness

If `tasks.md` exists in the change, count incomplete tasks (`- [ ]`). If any remain, warn the user and confirm before proceeding. Archiving a half-finished change leaves reference specs describing behavior that isn't actually built.

If applicable, confirm the change's tests pass before archiving.

### 2. Show sync summary

For each directory in `specs/changes/<slug>/deltas/`:

- Read the spec delta
- Read the corresponding `specs/reference/<same-name>/spec.md` (if it exists)
- Summarize what would change: requirements ADDED / MODIFIED / REMOVED / RENAMED per capability
- Present the summary to the user

The user should see exactly what the reference specs will look like after merge, at a high level, before you merge anything.

### 3. Merge deltas into reference specs

Invoke the **spexl-spec-sync agent** with the change directory path and spec root. The agent handles all delta-to-reference merging (ADDED, MODIFIED, REMOVED, RENAMED) and creates new capability specs as needed.

```
"Merge the spec deltas from {change-dir} into the reference specs. Spec root: {spec-root}"
```

Do not merge inline. The merge is mechanical work that belongs in a subagent to keep the main context clean.

When a new capability is being created, spexl-spec-sync will use the reference-spec structure from the methodology skill's spec notation.

### 4. Validate merged specs

Invoke the **spexl-spec-critic agent** in `inter-spec` mode on the updated reference specs. The merge is mechanical -- the critic checks that the result makes sense and doesn't contradict itself or other specs.

```
"Review the reference specs after the {slug} merge. Mode: inter-spec."
```

If the critic returns `needs-work` or `blocked`, fix the reference specs before proceeding. Do not archive a change that leaves the reference in a broken state.

### 5. Move to archive

```
specs/changes/<slug>/ → specs/changes/archive/YYYY-MM-DD-<slug>/
```

The date prefix uses today's date (UTC) for consistency. `spexl archive <slug>` handles this if available.

Archive keeps the change history browsable without cluttering the active-changes list.

## Key Principle

Reference specs describe how things work *now*, not how they changed. The archived change directory preserves the history: the proposal (why), the deltas (what changed), the design (how), and the tasks (what was done).

## Do Not

- Archive a change with failing tests or incomplete tasks without explicit user confirmation
- Merge deltas inline -- always use the spexl-spec-sync agent
- Skip the inter-spec critic validation
- Modify the archived change folder after moving -- it's history, treat it as read-only
