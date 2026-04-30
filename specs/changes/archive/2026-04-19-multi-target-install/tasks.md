## 1. Content restructuring

- [ ] Create `src/spexl/content/templates/` directory structure
- [ ] Convert existing skills, agents, and onboard content to Jinja2 templates
- [ ] Add per-target conditionals where content varies (tool references, phrasing)
- [ ] Create rules template (`sdd-with-spexl.md.j2`) from current `onboard.md` content
- [ ] Create hook templates per target (Claude settings.json entries, opencode plugin, pi extension)

## 2. Install command rewrite

- [ ] Change argparse: `--target`/`-t` flag replaces positional `target` argument
- [ ] Add target registry with destination mappings per target (claude, opencode, pi)
- [ ] Implement Jinja2 template rendering with per-target context
- [ ] Implement managed-file marker injection (per file type)
- [ ] Implement Claude-specific settings.json merge for hooks
- [ ] Implement file-drop for opencode/pi hooks
- [ ] Update refresh logic to work with rendered content comparison
- [ ] Update `--remove` to handle settings.json hook cleanup and multi-target
- [ ] Add `jinja2` to pyproject.toml dependencies

## 3. Remove onboard command

- [ ] Remove `cli/steering.py`
- [ ] Remove `steering` module registration from `__init__.py`
- [ ] Add friendly error for `spexl onboard` suggesting `spexl install -t <target>`
- [ ] Remove `content/onboard.md` (content migrated to rules template)

## 4. Config updates

- [ ] Ensure `.spexl.toml` `[agents.<target>]` sections record per-target install paths correctly
- [ ] Handle targets that split across two directories (e.g., opencode: `.agents/` + `.opencode/`)

## 5. Verification

- [ ] Tests for requirement: install-target (all three targets)
- [ ] Tests for requirement: template-rendering
- [ ] Tests for requirement: managed-file-marker
- [ ] Tests for requirement: per-target-destination-mapping
- [ ] Tests for requirement: claude-hook-installation
- [ ] Tests for requirement: rules-file-generation
- [ ] Tests for requirement: methodology-skill
- [ ] Tests for requirement: agent-generation
- [ ] Tests for requirement: install-command (CLI surface)
- [ ] Tests for requirement: onboard-removal (friendly error)

## Notes

- Jinja2 becomes a runtime dependency. It's pure Python and lightweight.
- The `.agents/` directory is shared between opencode and pi for skills and rules. The install command must handle this cleanly when both targets are configured.
- Claude Code settings.json mutation is the highest-risk area. Needs backup/validate/write pattern.
