# Changelog

## [Unreleased]

### Changed

- **BREAKING** removed `spexl install` and `spexl prime` (and the legacy `spexl onboard` stub). Skills, subagents, and the SessionStart primer ship as a Claude Code plugin: `skills/`, `agents/`, `plugins/claude/hooks/`, and `.claude-plugin/plugin.json` at the repo root. Install via Claude Code's plugin mechanism, not the CLI.
- Plugin content is now rendered from `.shablon/templates/` by [shablon](https://github.com/a3lem/shablon). Edit templates, run `just plugins` (= `shablon generate`), commit both. The SessionStart hook `cat`s `plugins/claude/hooks/prime.md` -- no Python in the priming path.
- Removed `install_targets` from `.spexl.toml`. The legacy `[agents.*]` table migration is also gone.
- Removed `src/spexl/content/` and the `spexl.cli.install`/`spexl.cli.steering` modules. `cmd_init` lives in `spexl.cli.init`.
- Renamed the methodology skill from `spexl-how-to-use` to `spexl-foundations`. Action skills and agents defer to the new name.
- Rewrote the foundations skill body to introduce specifications and spec deltas first, then the CLI and reference index -- so a reader learning what spec-driven development *is* doesn't land in a lookup table.
- `spexl init` is idempotent: running it in an existing project creates missing `specs/` directories and leaves existing files untouched. Passing a positional argument (e.g. `spexl init claude`) errors with guidance to use the plugin mechanism.

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
