# spexl

Spec-driven development for evolving codebases.

spexl manages behavioral specifications alongside your code. Specs describe what the system does using requirements and scenarios. When something needs to change, you propose a *spec delta* -- a structured diff against the current spec -- then implement against it, then merge the delta back into the reference. The spec stays the source of truth throughout.

The approach draws heavily from [openspec](https://github.com/nicobailon/openspec). Where spexl differs: it supports monorepos (multiple spec roots in one project), provides runtime steering for AI agents during implementation, and generates self-contained skill files so agents can work the full propose-apply-archive lifecycle without external context.

## Install

```
uv tool install git+https://github.com/a3lem/spexl
```

## Getting started

Initialize a project:

```
cd your-project
spexl init
```

This creates `.spexl.toml` and the `specs/` directory structure:

```
specs/
├── reference/          # Source of truth -- how the system behaves now
│   └── <capability>/spec.md
└── changes/
    ├── archive/        # Completed changes
    └── <slug>/         # Active changes
        ├── proposal.md
        ├── deltas/<capability>/spec.md
        ├── design.md
        ├── tasks.md
        └── notes/
```

## CLI

```
usage: spexl [-h] [--version] [--cwd PROJECT_DIR] command
```

### Spec management

These commands handle the filesystem operations around specs and changes.

| Command | What it does |
|---------|-------------|
| `new <slug>` | Scaffold a new change directory |
| `changes` | List active changes (grouped by spec root in monorepos) |
| `info <slug>` | Show change overview -- artifacts, deltas, task progress, links |
| `archive <slug>` | Merge deltas into reference specs, move change to archive |
| `validate` | Check all changes for structural problems |
| `refs` | List reference specs |
| `link <a> <b>` | Link two changes across spec roots |
| `unlink <a> <b>` | Remove a link |

### Knowledge serving

These commands print content to stdout. They exist so AI agents (and humans) can pull methodology guidance on demand without bundling everything into the system prompt.

| Command | What it does |
|---------|-------------|
| `prime` | Print foundational spexl knowledge for system prompt injection |
| `explain <topic>` | Deep guidance on a specific technique |
| `template <type>` | Print an artifact scaffold |

Available topics (`spexl explain --list`):

```
critique             Spec-critic checklists and modes
design               Guidance for writing design documents
spec-notation        Notation and structure for spec deltas
spexl                Full SDD methodology overview
tasks                Guidance for writing task breakdowns
verification         Test strategies and annotation conventions
```

Available templates (`spexl template --list`):

```
design               Design document (context, decisions, risks)
proposal             Proposal (why, what changes, capabilities, impact)
reference-spec       Reference spec (overview, requirements, scenarios)
spec-delta           Spec delta (ADDED/MODIFIED/REMOVED requirements)
tasks                Task breakdown (checkboxes, phases)
```

### Agent integration

| Command | What it does |
|---------|-------------|
| `init claude` | Install or refresh Claude Code integration files |
| `init --remove` | Remove all spexl-managed files |

Running `init` again after an spexl upgrade refreshes all generated files. It's idempotent -- files are only written when content has changed.

## AI agent support

spexl is designed for AI agents as first-class users. All errors exit 1 with an explanation the agent can reason about.

Currently supported: [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

### Installing for Claude Code

```
spexl init claude
```

This installs into `.claude/`:

```
.claude/
├── rules/
│   └── spexl.md                    # Foundational knowledge (always loaded)
├── agents/
│   ├── spec-critic.md              # Adversarial spec reviewer
│   └── spec-sync.md                # Delta-to-reference merger
└── skills/
    ├── spexl-explore/SKILL.md      # /explore -- investigate before proposing
    ├── spexl-propose/SKILL.md      # /propose -- create a change with all artifacts
    ├── spexl-refine/SKILL.md       # /refine  -- update any existing artifact
    ├── spexl-apply/SKILL.md        # /apply   -- implement and verify against spec
    └── spexl-archive/SKILL.md      # /archive -- merge deltas, move to archive
```

Each skill is self-contained -- all methodology knowledge is composed into the file at generation time. No runtime dependencies beyond the `spexl` CLI itself.

### Workflow

The five skills map to the spec-driven lifecycle:

```
/explore  → Read code, ask questions, investigate. No implementation.
/propose  → Create a change: proposal, spec deltas, optionally design + tasks.
/refine   → Update any artifact in an existing change.
/apply    → Implement the change. Verify against every requirement and scenario.
/archive  → Merge deltas into reference specs. Done.
```

Phases can be revisited. An implementation snag might reveal a spec gap; go back to `/refine`, then `/apply` again.

### Sub-agents

Two sub-agents are installed alongside the skills:

- **spec-critic** -- Reviews specs for internal coherence, code alignment, and cross-spec consistency. Invoked automatically during `/propose` and `/refine`.
- **spec-sync** -- Handles the mechanical work of merging deltas into reference specs during `/archive`.

## Configuration

spexl uses a `.spexl.toml` file at the project root. Minimal config:

```toml
[agents.claude]
install_path = ".claude/"
```

The `specs_location` section is optional and defaults to `./specs`:

```toml
[specs_location]
dir_path = "./specs"
changes_dir = "changes"
reference_dir = "reference"
```

For monorepos, each sub-project gets its own `.spexl.toml` and `specs/` directory. The CLI discovers configs by walking up from `--cwd` (or the current directory), and walks down to find nested spec roots.

## Acknowledgements

spexl draws on ideas from other spec-driven development tools and writing:

- [openspec](https://github.com/nicobailon/openspec) -- the closest predecessor; the delta-then-merge workflow comes from here
- [kiro](https://kiro.dev/docs/)
- [spec-kit](https://github.com/github/spec-kit)
- [SDD tools (Fowler)](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)

## License

MIT
