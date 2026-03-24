# Changelog

## [0.1.0] - 2026-03-24

### Plumbing

- `new <slug>` – scaffold a new change directory with `.change.json` and `deltas/`
- `changes` – list active changes grouped by spec root, with computed status (`drafting`, `ready`, `in progress`, `complete`)
- `changes --archived` / `--all` – filter to archived or show both active and archived
- `changes --linked` – filter to changes with cross-project links
- `info <identifier>` – show change overview (artifacts, deltas, tasks, links); resolves by slug, id, or path
- `archive <slug>` – archive a completed change with sync summary; supports `--dry-run`, `--rejected`, `--force`
- `refs` – list reference specs grouped by spec root
- `refs --long` – include overview descriptions
- `validate` – check changes for structural problems
- `link <a> <b>` / `unlink <a> <b>` – manage cross-project change links

### Skill Generation

- `init claude` – install or refresh spexl agent integration files (skills, agents, rules, hooks)
- `prime` – print foundational spexl knowledge for system prompt injection

### Runtime Steering

- `explain <topic>` – deep guidance on spec-notation, design, tasks, verification, critique
- `template <type>` – artifact scaffolding for proposal, spec-delta, reference-spec, design, tasks

### Infrastructure

- `.spexl.toml`-based project discovery with recursive walk-down across monorepo sub-projects
- `--cwd` flag on all commands for explicit project root
- `--json` output on `changes`, `info`, `refs`
- `--no-recurse` flag to restrict to nearest config
- ID resolution across all discovered spec roots
- Computed status from artifact presence and task completion
