# Tasks Guidance

How to create and maintain `tasks.md` as a lightweight progress overview.

## Purpose

`tasks.md` is a progress overview -- a high-level checklist of what needs doing and what's done. It is not an execution plan or implementation guide.

## When to Create

- **Directory specs** with 3+ implementation steps or multi-session work
- **Skip** for simple specs where the spec itself is sufficient

Create during the propose phase, after spec and design are complete.

## Structure

Group tasks by phase or component using checkboxes:

```markdown
## API Layer

- [ ] Add authentication endpoint
- [ ] Add token refresh endpoint (TK-042)
- [x] Define error response format

## Database

- [ ] Create users table migration
- [ ] Add session tracking table
```

### Ticket References

Reference external tickets inline when they exist:

```markdown
- [ ] Implement rate limiting (TK-015)
```

Ticket references are optional. Only add them when a task maps to an existing ticket.

### Notes Section

Use a Notes section at the bottom for blockers, dependencies, or context:

```markdown
## Notes

- Blocked on API key provisioning from infrastructure team
- Database migrations must run before API deployment
```

### Verification Section

Every `tasks.md` should include a Verification section with test-writing tasks. These tasks are what stand between `in progress` and `complete`.

```markdown
## Verification

- [ ] Tests for requirement: create-change
- [ ] Tests for requirement: list-active-changes
- [ ] Tests for requirement: archive-change
```

One task per requirement. Each task is done when the requirement has at least one annotated test (see `verification.md`).

## What Belongs in tasks.md

- Task groupings by phase or component
- A Verification section with per-requirement test tasks
- Checkboxes showing completion status
- Optional ticket references
- Blockers and dependencies

## What Does NOT Belong

- Detailed implementation steps (those belong in `design.md` or `notes/`)
- `[NEXT]` markers or execution state
- Restatements of spec scenarios

## Updating tasks.md

- **Propose phase**: Create the initial task breakdown
- **Apply phase**: Check off tasks as they are completed (checkboxes only -- don't restructure during execution)

## Relationship to Ticket Systems

When the project uses an external ticket CLI, `tasks.md` can reference ticket numbers inline. The `tasks.md` file provides a spec-scoped view of progress, while the ticket system tracks the broader project backlog.
