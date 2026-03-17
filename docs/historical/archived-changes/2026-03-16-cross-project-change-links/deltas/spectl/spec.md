# spectl

## ADDED Requirements

### Requirement: Link changes

The system SHALL create bidirectional links between two changes when `spectl link <change-a> <change-b>` is invoked. Both arguments are paths to change directories (absolute or relative to cwd).

#### Scenario: Basic link
  Given change A at `services/api/specs/changes/add-oauth/` with id `abc12`
  And change B at `libs/auth/specs/changes/add-token-refresh/` with id `def34`
  When the user runs `spectl link services/api/specs/changes/add-oauth libs/auth/specs/changes/add-token-refresh`
  Then A's `.change.json` gains `"links": [{"specs": "../../libs/auth/specs", "change": "def34"}]`
  And B's `.change.json` gains `"links": [{"specs": "../../services/api/specs", "change": "abc12"}]`

#### Scenario: Idempotent link
  Given change A already links to change B
  When the user runs `spectl link` with the same arguments
  Then no duplicate link entry is added
  And the command exits 0

#### Scenario: Link to nonexistent change
  When the user runs `spectl link services/api/specs/changes/add-oauth nonexistent/path`
  Then the command exits with an error indicating the path does not exist

#### Scenario: Spec root derivation
  Given a change path `services/api/specs/changes/add-oauth/`
  When the system derives the spec root
  Then it returns `services/api/specs/` (parent of parent of the change directory)

### Requirement: Unlink changes

The system SHALL remove the link between two changes when `spectl unlink <change-a> <change-b>` is invoked.

#### Scenario: Basic unlink
  Given change A links to change B and B links back to A
  When the user runs `spectl unlink <change-a-path> <change-b-path>`
  Then A's `.change.json` no longer contains the link to B
  And B's `.change.json` no longer contains the link to A

#### Scenario: Unlink nonexistent link
  Given change A has no link to change B
  When the user runs `spectl unlink <change-a-path> <change-b-path>`
  Then the command exits 0 without error

#### Scenario: Empty links array cleanup
  Given change A's only link was to change B
  When the user runs `spectl unlink <change-a-path> <change-b-path>`
  Then the `links` field is removed from A's `.change.json` entirely
  And the `links` field is removed from B's `.change.json` entirely

### Requirement: Validate links

The system SHALL check link integrity when `spectl validate` is invoked.

#### Scenario: Broken link detected
  Given change A has a link with specs path `../../libs/auth/specs` and change id `def34`
  And `../../libs/auth/specs` does not exist
  When the user runs `spectl validate`
  Then the output reports a broken link error for A
  And the command exits 1

#### Scenario: Broken link to missing change
  Given change A has a link to specs path `../../libs/auth/specs` which exists
  But no change in that specs directory has id `def34`
  When the user runs `spectl validate`
  Then the output reports a broken link error for A
  And the command exits 1

#### Scenario: Asymmetric link detected
  Given change A links to change B
  But change B does not link back to A
  When the user runs `spectl validate`
  Then the output reports an asymmetric link error
  And the command exits 1

#### Scenario: Fix asymmetric link
  Given change A links to change B but B does not link back to A
  When the user runs `spectl validate --fix`
  Then B's `.change.json` gains a link back to A
  And the fix is reported in output

## MODIFIED Requirements

### Requirement: Change info

The system SHALL compute and display an overview of a change when `spectl info <identifier>` is invoked. The identifier can be a slug, an id, or a path. WHEN the change has links, the system SHALL resolve and display them.

#### Scenario: Resolve by path
  When the user runs `spectl info specs/changes/add-oauth`
  Then the change is resolved directly from the path

#### Scenario: Resolve by slug or id (active)
  When the user runs `spectl info add-oauth` or `spectl info x7k2m`
  Then the change is resolved by scanning active changes in `specs/changes/`

#### Scenario: Resolve by slug or id (archived)
  When the user runs `spectl info add-oauth --archived` or `spectl info x7k2m --archived`
  Then the change is resolved by also scanning `specs/changes/archive/`

#### Scenario: Info output
  Given a change `add-oauth` with proposal.md, design.md, deltas/user-auth/spec.md, and tasks.md with 3/5 tasks complete
  When the user runs `spectl info add-oauth`
  Then the output shows:
  ```
  add-oauth (x7k2m)
  created: 2026-03-14
  artifacts: proposal.md, design.md, tasks.md
  deltas: user-auth
  tasks: 3/5 complete
  ```

#### Scenario: Info with --json
  When the user runs `spectl info add-oauth --json`
  Then the output is a JSON object with id, created, artifacts list, deltas list, and task counts

#### Scenario: Info for archived change
  Given an archived change with `archived: {"reason": "merged"}` in `.change.json`
  When the user runs `spectl info specs/changes/archive/2026-03-14-add-oauth`
  Then the output includes `archived: merged`

#### Scenario: No match
  When the user runs `spectl info nonexistent`
  Then the command exits with an error indicating no change matched the identifier

#### Scenario: Info with resolved links
  Given a change `add-oauth` (id: `abc12`) links to change `add-token-refresh` (id: `def34`) at `../../libs/auth/specs`
  And `add-token-refresh` has status `in progress`
  When the user runs `spectl info add-oauth`
  Then the output includes:
  ```
  links:
    def34 [in progress] add-token-refresh (../../libs/auth/specs)
  ```

#### Scenario: Info with broken link
  Given a change `add-oauth` links to change id `def34` at `../../libs/auth/specs`
  And the link cannot be resolved (specs dir missing or change id not found)
  When the user runs `spectl info add-oauth`
  Then the output includes:
  ```
  links:
    def34 [broken] (../../libs/auth/specs)
  ```

#### Scenario: Info with links as JSON
  Given a change with a resolvable link
  When the user runs `spectl info add-oauth --json`
  Then the JSON output includes a `links` array with `specs`, `change`, `slug`, and `status` fields

#### Scenario: Info with broken link as JSON
  Given a change with a broken link
  When the user runs `spectl info add-oauth --json`
  Then the JSON `links` array entry has `"status": "broken"` and no `slug` field

### Requirement: Archive change

The system SHALL check completeness, print a sync summary, and move the change to archive when `spectl archive <identifier>` is invoked. Merging deltas into reference specs is handled by the spec-sync agent, not by spectl. WHEN the change has links, the system SHALL warn about linked changes that are still active.

#### Scenario: Sync summary
  Given a change `add-oauth` with deltas for `user-auth` (1 ADDED, 2 MODIFIED) and `oauth-provider` (3 ADDED, new capability)
  When the user runs `spectl archive add-oauth`
  Then the output shows:
  ```
  Sync summary:
    user-auth: 1 added requirement, 2 modified requirements
    oauth-provider: NEW capability (3 added requirements)
  ```

#### Scenario: Move to archive
  Given today is 2026-03-14
  When the user runs `spectl archive add-oauth`
  Then `specs/changes/add-oauth/` is moved to `specs/changes/archive/2026-03-14-add-oauth/`
  And `.change.json` gains an `archived` field: `{"reason": "merged"}`

#### Scenario: Incomplete tasks guard
  Given `tasks.md` exists with 2 incomplete tasks
  When the user runs `spectl archive add-oauth`
  Then the command exits with an error "2 incomplete tasks remain" and exit code 1

#### Scenario: Force archive with incomplete tasks
  Given `tasks.md` exists with incomplete tasks
  When the user runs `spectl archive add-oauth --force`
  Then the archive proceeds despite incomplete tasks

#### Scenario: Reject a change
  When the user runs `spectl archive add-oauth --rejected`
  Then `.change.json` gains `{"archived": {"reason": "rejected"}}`
  And the change is moved to `specs/changes/archive/2026-03-14-add-oauth/`
  But no sync summary is printed

#### Scenario: Dry run
  When the user runs `spectl archive add-oauth --dry-run`
  Then the sync summary is printed
  But no files are moved

#### Scenario: Archive with active linked changes
  Given change `add-oauth` links to change `add-token-refresh` (id: `def34`, status: `in progress`) at `../../libs/auth/specs`
  When the user runs `spectl archive add-oauth`
  Then the output includes:
  ```
  Linked changes still active:
    def34 [in progress] add-token-refresh (../../libs/auth/specs)
  ```
  And the archive proceeds (warning only, not blocking)

#### Scenario: Archive with broken linked change
  Given change `add-oauth` has a link that cannot be resolved
  When the user runs `spectl archive add-oauth`
  Then the output includes a warning about the broken link
  And the archive proceeds

#### Scenario: Archive rejected with active linked changes
  Given change `add-oauth` links to an active change
  When the user runs `spectl archive add-oauth --rejected`
  Then the linked-changes warning is still printed

### Requirement: Validate changes

The system SHALL check changes for structural problems when `spectl validate` is invoked. By default it reports issues and exits 1 if any are found. With `--fix`, it repairs what it can. This includes checking link integrity.

#### Scenario: Missing id
  Given a change has `.change.json` without an `id` field
  When the user runs `spectl validate`
  Then the output reports the missing id and exits 1

#### Scenario: Fix missing id
  Given a change has `.change.json` without an `id` field
  When the user runs `spectl validate --fix`
  Then an id is generated and written to `.change.json`

#### Scenario: Missing created date
  Given a change has `.change.json` without a `created` field
  When the user runs `spectl validate`
  Then the output reports the missing date and exits 1

#### Scenario: Fix missing created date
  Given a change has `.change.json` without a `created` field
  When the user runs `spectl validate --fix`
  Then `created` is set to today's date

#### Scenario: Archived merged change with open tasks
  Given an archived change with reason `merged` has open tasks in `tasks.md`
  When the user runs `spectl validate`
  Then the output reports the inconsistency and exits 1

#### Scenario: All valid
  When the user runs `spectl validate` and no issues are found
  Then the output reports success and exits 0

#### Scenario: Broken link detected
  Given an active change has a link whose specs path does not resolve to an existing directory
  When the user runs `spectl validate`
  Then the output reports the broken link and exits 1

#### Scenario: Broken link to missing change
  Given an active change has a link whose specs path exists but contains no change with the referenced id
  When the user runs `spectl validate`
  Then the output reports the broken link and exits 1

#### Scenario: Asymmetric link detected
  Given change A links to change B but B does not link back to A
  When the user runs `spectl validate`
  Then the output reports the asymmetric link and exits 1

#### Scenario: Fix asymmetric link
  Given change A links to change B but B does not link back to A
  When the user runs `spectl validate --fix`
  Then B gains a back-link to A in its `.change.json`
  And the fix is reported
