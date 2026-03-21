---
name: project_architecture
description: spexl's three-role architecture (spec management, skill generation, runtime steering) and per-domain CLI module structure
type: project
---

spexl has three roles:
1. **Spec management** – `new`, `changes`, `archived`, `info`, `archive`, `validate`, `refs`, `link`, `unlink`
2. **Skill generation** – `init claude`, `update` (compose partials + actions into self-contained SKILL.md files)
3. **Runtime steering** – `prime` (foundational methodology), `explain <topic>` (advanced knowledge on demand), `template <artifact>` (artifact scaffolding)

CLI modules are split by domain, not by arbitrary groupings:
- `cli/changes.py` – change lifecycle
- `cli/links.py` – cross-project linking
- `cli/validate.py` – structural validation
- `cli/refs.py` – reference spec listing
- `cli/generate.py` – init, update
- `cli/steering.py` – context, template

Shared helpers live in `specroot.py` (spec root discovery, change resolution, .change.json I/O). Error type in `errors.py`. Template access via `templates.py` using `importlib.resources`.

Templates are package data at `src/spexl/templates/` (not top-level). Accessed via `importlib.resources.files("spexl.templates")`.

**How to apply:** When adding new CLI commands, create a new module if they represent a new domain. Don't add to an existing module unless it's the same domain. Each module exposes `register(subparsers)`.
