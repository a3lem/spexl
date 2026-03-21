# Archive Phase Reference

How to archive a completed change by merging deltas into reference specs.

## Process

### 1. Check Completeness

If `tasks.md` exists, count incomplete tasks (`- [ ]`). Warn the user and confirm before proceeding if any remain.

### 2. Show Sync Summary

For each directory in `change-dir/deltas/`:
- Read the spec delta
- Read the corresponding `specs/reference/<same-name>/spec.md` (if it exists)
- Summarize what would change: requirements ADDED / MODIFIED / REMOVED per capability
- Present this summary to the user

### 3. Merge Deltas into Reference Specs

Invoke the **spec-sync agent** with the change directory path and spec root. The agent handles all delta-to-reference merging (ADDED, MODIFIED, REMOVED, RENAMED) and creates new capability specs as needed. Run `spexl template reference-spec` for the reference spec template when creating new capabilities.

```
"Merge the spec deltas from {change-dir} into the reference specs. Spec root: {spec-root}"
```

Do not merge inline. The merge is mechanical work that belongs in a subagent to keep the main context clean.

### 4. Validate Merged Specs

Invoke **spec-critic agent** (`inter-spec` mode) on the updated reference specs. The merge is mechanical -- the critic checks that the result makes sense and doesn't contradict itself. If the critic returns `needs-work` or `blocked`, fix the reference specs before proceeding.

### 5. Move to Archive

`specs/changes/slug/` → `specs/changes/archive/YYYY-MM-DD-slug/`

Archive keeps the change history browsable without cluttering active specs.

## Key Principle

Reference specs should describe how things work *now*, not how they changed. The archived change directory preserves the history.
