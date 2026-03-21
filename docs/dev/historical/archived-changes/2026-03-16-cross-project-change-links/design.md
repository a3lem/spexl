## Context

`spectl` manages change lifecycle within a single `specs/` directory. In monorepos, each sub-project has its own `specs/` directory, and `spectl changes -r` discovers them all. But there's no mechanism to express that a change in one project is related to a change in another. This design adds cross-project linking to `.change.json` and the `spectl` commands that read it.

## Goals / Non-Goals

**Goals:**
- Express "these two changes go together" across spec roots
- Make links bidirectional (both sides know about each other)
- Surface links in existing commands (info, archive, validate)
- Keep it mechanical -- no judgment calls, no ordering semantics

**Non-Goals:**
- Dependency ordering (apply A before B). The build/test system handles this.
- Transitive link resolution (A links B, B links C, therefore A relates to C). One hop is enough.
- Enforcing that linked changes archive together. Warn, don't block.

## Decisions

### Link data model

A `links` field in `.change.json`, containing an array of link objects:

```json
{
  "id": "abc12",
  "created": "2026-03-16",
  "links": [
    {"specs": "../../libs/auth/specs", "change": "def34"}
  ]
}
```

`specs` is a relative path from the current `specs/` directory to the linked `specs/` directory. `change` is the target change's ID (from its `.change.json`). Using the ID rather than the slug means links survive slug renames.

The path is always relative to the current spec root, because there's no guaranteed project root marker. `spectl` resolves it as `current_spec_root / link["specs"]`.

**Alternatives considered:** A `group` field with a shared string identifier. Simpler, but unvalidatable -- a typo silently disconnects changes, and there's no path for `spec-critic` to follow. Paths + IDs give tooling something concrete to resolve.

### `spectl link` command

```
spectl link <change-a> <change-b>
```

Both arguments are change paths (absolute or relative to cwd), like `services/api/specs/changes/add-oauth`. The command:

1. Resolves both paths to change directories
2. Reads both `.change.json` files to get IDs
3. Derives each change's spec root by walking up from the change directory to find the `specs/` ancestor (the parent of `changes/`)
4. Computes the relative path from spec root A to spec root B, and vice versa
5. Adds a link entry to each `.change.json` (idempotent -- skips if the link already exists)

Spec root derivation: from a change path like `services/api/specs/changes/add-oauth/`, walk up until we find a directory whose name is not `changes` and that contains a `changes/` child. In practice: `change_path.parent` is `changes/`, `change_path.parent.parent` is the spec root. This works for both active (`specs/changes/slug/`) and the expected structure.

**Alternatives considered:** A `--dir` flag on `link` to specify spec roots explicitly. Unnecessary -- the change paths already contain enough information to derive the spec roots.

### `spectl unlink` command

```
spectl unlink <change-a> <change-b>
```

Same resolution as `link`. Removes the link entry from both sides. No error if the link doesn't exist (idempotent).

### Changes to `spectl info`

When a change has `links`, `info` resolves each link and shows:

```
add-oauth (abc12)
created: 2026-03-16
artifacts: proposal.md, design.md, tasks.md
deltas: user-auth
tasks: 3/5 complete
links:
  def34 [in progress] add-token-refresh (../../libs/auth/specs)
```

Each link line shows: ID, status, slug, and the specs path. If the link can't be resolved (specs dir missing or change ID not found), show the raw link data with a `[broken]` marker:

```
links:
  def34 [broken] (../../libs/auth/specs)
```

For `--json` output, links are included in the JSON object with resolved data where possible:

```json
{
  "links": [
    {"specs": "../../libs/auth/specs", "change": "def34", "slug": "add-token-refresh", "status": "in progress"}
  ]
}
```

Broken links include `"status": "broken"` and omit `slug`.

### Changes to `spectl archive`

After the sync summary (and before moving files), if the change has links, resolve each one and warn about non-archived linked changes:

```
Linked changes still active:
  def34 [in progress] add-token-refresh (../../libs/auth/specs)
```

This is a warning, not a blocker. The archive proceeds. Rationale: the user may legitimately archive one side first (e.g., the library change is ready, the service change isn't). Blocking would be more annoying than helpful.

`--rejected` also prints the warning. Even a rejected change might have a companion that needs attention.

### Changes to `spectl validate`

Two new checks:

1. **Broken links:** For each link in each active change, verify the specs directory exists and contains a change with the matching ID. Report as error if not.

2. **Asymmetric links:** If change A links to change B, change B should link back to change A. Report as error if not. With `--fix`, add the missing back-link.

### Link resolution helper

A shared `resolve_link(spec_root, link)` function used by `info`, `archive`, and `validate`:

```python
def resolve_link(spec_root, link):
    """Resolve a link to a (change_path, change_json) tuple, or None if broken."""
    target_root = (spec_root / link["specs"]).resolve()
    target_changes = target_root / "changes"
    if not target_changes.is_dir():
        return None
    for d in target_changes.iterdir():
        if not d.is_dir() or d.name == "archive":
            continue
        cj = d / ".change.json"
        if cj.is_file():
            data = read_change_json(cj)
            if data.get("id") == link["change"]:
                return (d, data)
    return None
```

### Spec root derivation from change path

```python
def derive_spec_root(change_path):
    """Derive the spec root from a change directory path.

    Expects: .../specs/changes/slug/ → returns .../specs/
    """
    # change_path.parent is changes/, parent.parent is specs/
    return change_path.parent.parent
```

This is simple because the directory structure is fixed: `specs/changes/<slug>/`. No searching needed.

## Risks / Trade-offs / Limitations

Relative paths in `links` break if spec directories are moved relative to each other → `validate` catches this. In practice, monorepo directory structures rarely change.

No transitive resolution means a three-way cross-project change requires explicit links between all pairs → Acceptable. Three-way changes are rare, and explicit links are clearer than implicit transitive chains.

Archive warnings are non-blocking → A user could forget about the companion change. Mitigation: `spectl changes -r` already surfaces all active changes; combined with the archive warning, this is enough.

Links reference change IDs, which are random strings → If `.change.json` is lost or corrupted, the link is unresolvable. `validate` catches this. The risk is low since `.change.json` is version-controlled.

## Open Questions

None.
