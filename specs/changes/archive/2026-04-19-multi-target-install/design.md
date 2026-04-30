## Context

spexl currently installs agent integration files for Claude Code only, copying bundled content verbatim from `src/spexl/content/{skills,agents}/`. The install command needs to support three targets (claude, opencode, pi) with per-target content differences and destination paths.

Key constraints from exploration:
- `.agents/` is agent-agnostic. No target-specific conditionals in content destined for `.agents/`. Claude Code doesn't read `.agents/`, so shared content must be copied to `.claude/` for that target.
- Hooks are out of scope for spexl (relevant for epimem/tiquette, not here).
- Subagent definitions are target-specific: full support for claude, partial for opencode (subset of frontmatter), none for pi.
- Rationale for the install-command approach over native plugins is documented in `docs/why-install-instead-of-plugins.md`.

## Goals / Non-Goals

**Goals:**
- Install spexl skills, rules, and agents for claude, opencode, and pi from a single CLI command
- Render per-target content from Jinja2 templates where needed
- Enforce the `.agents/` purity constraint at the template-layout level
- Replace the `onboard` command with an installed rules file
- Support `--inplace` to inject rules directly into CLAUDE.md/AGENTS.md

**Non-Goals:**
- Hook installation (out of scope for spexl)
- Runtime template rendering (all rendering happens at install time)
- Supporting targets beyond claude, opencode, pi in this change

## Decisions

### Target enum and destination registry

A `Target` enum defines the three supported targets. Each target has a `TargetConfig` that maps artifact types to destination directories:

```python
class Target(enum.StrEnum):
    CLAUDE = "claude"
    OPENCODE = "opencode"
    PI = "pi"

@dataclass(frozen=True)
class TargetConfig:
    skills_dir: Path
    rules_dir: Path
    agents_dir: Path | None  # None = target doesn't support agents
    shared_skills_dir: Path | None  # Where shared content goes (same as skills_dir for claude)

TARGET_REGISTRY: dict[Target, TargetConfig] = {
    Target.CLAUDE: TargetConfig(
        skills_dir=Path(".claude/skills"),
        rules_dir=Path(".claude/rules"),
        agents_dir=Path(".claude/agents"),
        shared_skills_dir=Path(".claude/skills"),  # claude gets shared content here too
    ),
    Target.OPENCODE: TargetConfig(
        skills_dir=Path(".opencode/skills"),  # opencode-specific skills, if any
        rules_dir=Path(".agents/rules"),
        agents_dir=Path(".opencode/agents"),
        shared_skills_dir=Path(".agents/skills"),
    ),
    Target.PI: TargetConfig(
        skills_dir=Path(".pi/skills"),  # pi-specific skills, if any
        rules_dir=Path(".agents/rules"),
        agents_dir=None,  # pi doesn't support subagents
        shared_skills_dir=Path(".agents/skills"),
    ),
}
```

The registry is the single source of truth for "where does artifact X go for target Y." Adding a new target means adding one entry here plus any target-specific templates.

**Alternatives considered:** A per-target adapter class (OpenSpec's approach). Overkill at three targets with no hook logic. A flat dict is simpler and sufficient. Can always upgrade to classes if per-target logic grows.

### Template directory layout

```
src/spexl/content/templates/
├── shared/                           # Agent-agnostic content → .agents/ (or .claude/ for claude)
│   ├── skills/
│   │   ├── spexl-foundations/
│   │   │   ├── SKILL.md.j2
│   │   │   └── references/
│   │   │       ├── rules.md          # Plain files (no templating needed)
│   │   │       ├── concepts.md
│   │   │       ├── spec-notation.md
│   │   │       ├── structure.md
│   │   │       ├── verification.md
│   │   │       ├── critique.md
│   │   │       ├── design-guidance.md
│   │   │       ├── tasks-guidance.md
│   │   │       └── modes.md
│   │   ├── spexl-explore/SKILL.md.j2
│   │   ├── spexl-propose/SKILL.md.j2
│   │   ├── spexl-refine/SKILL.md.j2
│   │   ├── spexl-apply/SKILL.md.j2
│   │   └── spexl-archive/SKILL.md.j2
│   └── rules/
│       └── sdd-with-spexl.md.j2      # Methodology primer (replaces onboard.md)
├── claude/                            # Claude-specific content → .claude/
│   └── agents/
│       ├── spexl-spec-critic.md.j2
│       └── spexl-spec-sync.md.j2
└── opencode/                          # opencode-specific content → .opencode/
    └── agents/
        ├── spexl-spec-critic.md.j2    # Subset of frontmatter fields
        └── spexl-spec-sync.md.j2
```

Rules:
- Files ending in `.j2` are rendered through Jinja2. All others are copied verbatim.
- `shared/` content MUST NOT contain target-specific branches (`{% if target == ... %}`). This is enforced by convention (and can be validated in CI by grepping templates).
- Target-specific directories (`claude/`, `opencode/`, `pi/`) may use the full template context.
- If a skill needs target-specific phrasing (e.g., "use AskUserQuestion" vs "ask the user"), it moves out of `shared/` into each target directory. Prefer rewriting to agent-agnostic intent to keep it shared.

**Alternatives considered:** Flat layout with all templates in one directory and conditionals throughout. Rejected because it violates the `.agents/` purity constraint -- you'd need runtime checks to prevent conditional templates from landing in `.agents/`. The nested layout makes the constraint structural.

### Rendering pipeline

```
for each target:
    1. Enumerate shared/ templates → map to target's shared_skills_dir / rules_dir
    2. Enumerate <target>/ templates → map to target's skills_dir / agents_dir
    3. For each (template_path, dest_path):
       a. If .j2 extension: render with Jinja2, strip .j2 from dest filename
       b. Else: read verbatim
       c. Prepend managed-file marker
       d. Compare with existing file at dest_path
       e. Write if changed, skip if identical
    4. Prune files under managed directories that aren't in the expected set
```

The Jinja2 environment is configured once per install run:
- Loader: `PackageLoader("spexl.content", "templates")`
- Undefined: `StrictUndefined` (typos in template variables are fatal)
- Context for shared templates: `{"managed_marker": "..."}` (no `target` key -- enforces agnosticism)
- Context for target templates: `{"target": target.value, "managed_marker": "..."}`

**Key detail:** Shared templates get a context WITHOUT `target`. If a shared template accidentally references `{{ target }}`, Jinja2's StrictUndefined raises immediately. This enforces the `.agents/` purity constraint at render time, not just by convention.

### Content classification

| Content | Classification | Rationale |
|---------|---------------|-----------|
| spexl-foundations skill + references | Shared | Pure methodology prose, no agent-specific tools |
| Action skills (explore, propose, refine, apply, archive) | Shared (goal) | Rewrite to agent-agnostic intent where possible. If a skill unavoidably references agent-specific tools, move it to per-target. |
| Rules file (sdd-with-spexl.md) | Shared | Methodology primer, same for all agents |
| Agent definitions (spec-critic, spec-sync) | Target-specific | Frontmatter format differs: claude (full), opencode (subset), pi (none) |

If an action skill currently references `AskUserQuestion` or similar, it should be rewritten to "ask the user for clarification" or equivalent generic phrasing. The goal is to keep all skills in `shared/` and only split to per-target when the divergence is structural, not just wording.

### Rules installation modes

Two modes for the methodology primer:

**Default (file):** Write `sdd-with-spexl.md` to the target's rules directory. This is the standard path.

**`--inplace` flag:** Append the rules content to an existing file instead of creating a separate rules file. Target determines the file:
- claude → `CLAUDE.md`
- opencode, pi → `AGENTS.md`

The `--inplace` flag is useful when the target agent doesn't have a rules-loading mechanism (vanilla Claude Code without a rules-loader plugin, or agents that only read AGENTS.md).

Behavior:
- If the target file doesn't exist, create it with the rules content.
- If it exists, check whether spexl rules are already present (search for the managed marker). If found, replace the existing block. If not, append.
- The injected block is delimited by markers: `<!-- spexl:rules:start -->` and `<!-- spexl:rules:end -->`.
- `--remove` strips the delimited block from the file (and deletes the standalone rules file if present).

**Alternatives considered:** Only support `--inplace`, no separate rules file. Rejected because rules files are cleaner (no merge conflicts, no CLAUDE.md pollution) for agents that support them.

### Managed-file marker

Every generated file starts with a marker comment:

| File type | Marker |
|-----------|--------|
| Markdown (.md) | `<!-- managed by spexl - do not edit -->` |
| TOML | `# managed by spexl - do not edit` |
| YAML | `# managed by spexl - do not edit` |
| JS/TS | `// managed by spexl - do not edit` |

The marker serves two purposes:
1. Warn users against manual editing (changes will be overwritten on refresh).
2. Allow `--remove` to identify managed files (in addition to the `.spexl.toml` manifest).

For `--inplace` injected blocks, the start/end delimiters (`<!-- spexl:rules:start -->` / `<!-- spexl:rules:end -->`) serve the same identification purpose.

### Refresh and remove mechanics

**Refresh** (`spexl install -t <target>` when already installed):
1. Render all templates for the target.
2. Compare rendered content against existing files (byte comparison).
3. Overwrite changed files, skip identical ones.
4. Remove files under managed directories that are no longer in the template set.
5. Report counts: changed, unchanged, removed.

**Remove** (`spexl install --remove`):
1. Read `.spexl.toml` to find configured targets.
2. For each target, enumerate managed directories from the registry.
3. Delete all files with the managed-file marker under those directories.
4. If `--inplace` was used, strip the delimited rules block from CLAUDE.md/AGENTS.md.
5. Remove the `[agents]` section from `.spexl.toml` (do NOT delete the file).
6. Prune empty directories under managed paths.

**Tracking what was installed:** `.spexl.toml` records `[agents.<target>]` with `install_path`. The managed directories are derived from the `TargetConfig` registry. No separate manifest file needed -- the registry + `.spexl.toml` is sufficient.

**Shared directory conflict:** If both opencode and pi are installed, they share `.agents/skills/` and `.agents/rules/`. Shared content is identical regardless of target (same templates, no target context). Refresh for either target writes the same files. Remove for one target must NOT delete `.agents/` content if the other target is still configured. The remove logic checks `.spexl.toml` for remaining targets before pruning shared paths.

### .spexl.toml recording

```toml
[agents.claude]
install_paths = [".claude"]

[agents.opencode]
install_paths = [".agents", ".opencode"]

[agents.pi]
install_paths = [".agents", ".pi"]
```

Changed from singular `install_path` to `install_paths` (list) because opencode and pi write to two directories. The remove command iterates all paths. When checking whether a shared path (`.agents/`) can be pruned, it checks if any other configured target also lists that path.

### Onboard removal

`cli/steering.py` is deleted. The `onboard` subcommand is replaced with a stub in `__init__.py` that prints a friendly error:

```
'spexl onboard' has been removed. Use 'spexl install -t <target>' instead.
The methodology primer is now installed as a rules file automatically.
```

`content/onboard.md` is deleted. Its content migrates to `content/templates/shared/rules/sdd-with-spexl.md.j2`.

## Risks / Trade-offs / Limitations

**[Jinja2 runtime dependency]** → Jinja2 is pure Python, well-maintained, and lightweight (~150KB). The alternative (build-time rendering) would eliminate the dependency but require shipping pre-rendered variants for all targets in every package. At three targets this is acceptable either way; install-time rendering is chosen for flexibility.

**[Shared directory ownership]** → When both opencode and pi are configured, `.agents/` is managed by both. The remove logic must coordinate. Mitigated by checking `.spexl.toml` for remaining targets before pruning. Tested explicitly.

**[Action skill rewriting]** → Moving skills to agent-agnostic phrasing may reduce precision for specific agents. Mitigated by keeping the escape hatch: any skill that truly needs target-specific content moves to the per-target directory. The design makes this a file-move, not an architecture change.

**[install_paths schema change]** → `install_path` (string) → `install_paths` (list) is a breaking change to `.spexl.toml`. Mitigated by having install detect the old format and migrate it silently on refresh.

## Open Questions

- Should `spexl install` auto-detect which agents are present in the project (by scanning for `.claude/`, `.opencode/`, `.pi/` directories) and suggest targets? Or is explicit `--target` always required for first install?
