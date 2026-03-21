## 1. Agent definition

- [x] Create `agents/spec-sync.md` with frontmatter and merge instructions
- [x] Add merge algorithm steps (REMOVED → RENAMED → MODIFIED → ADDED)
- [x] Add error handling guidance (fallbacks + AskUserQuestion triggers)
- [x] Add example invocation and expected behavior

## 2. Integration

- [x] Update `references/archive.md` step 3 to delegate to spec-sync agent
- [x] Update `SKILL.md` sub-agents section to list spec-sync

## 3. Verification

- [x] Manual test: archive a change with ADDED requirements against new capability
- [x] Manual test: archive a change with MODIFIED/REMOVED against existing capability
- [x] Manual test: verify spec-critic validates merged result

## Notes

- No automated tests -- the deliverable is a prompt file, verified by invoking the agent and running spec-critic post-merge.
