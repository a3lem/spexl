# History

## Origins: spec-driven-dev plugin (Dec 2025 – Mar 2026)

spexl started as `spec-driven-dev`, a Claude Code plugin in a marketplace repo (`my-claude-plugins`). The idea: structured specifications drive development. You propose a change, write behavioral specs as deltas against reference specs, implement against those specs, then archive by merging deltas back into the reference.

The plugin had five slash commands (`/explore`, `/propose`, `/refine`, `/apply`, `/archive`), a monolithic SKILL.md with all methodology rules, reference documents for each phase, artifact templates, and two sub-agents (spec-critic for adversarial review, spec-sync for mechanical merges). A CLI script called `spectl` handled filesystem plumbing – creating change directories, validating structure, archiving.

It worked well when developing the plugin itself (dogfooding). Three changes were completed and archived: adding spectl, adding the spec-sync agent, and adding cross-project change links.

## The Loading Problem (Mar 2026)

Testing the plugin in a separate project revealed a fundamental issue. When a user invoked `/spec-driven-dev:propose`, Claude Code expanded the command file (18 lines of brief instructions) but never loaded the actual SKILL.md (164 lines of rules, routing, structure). The command told Claude to "use the spec-driven-development skill" in natural language, but since a `<command-name>` tag was already present, Claude assumed the skill was loaded and improvised from the brief command instructions alone.

The result looked plausible – Claude created spec directories and wrote artifacts – but it wasn't following the methodology. No templates were used, no rules were enforced, no phase-specific references were consulted.

## The Rewrite Decision

Three options were considered:

1. **Self-contained commands** – inline SKILL.md into each command file. Duplicates ~160 lines across 5 files.
2. **Commands that explicitly load the skill** – add Read instructions to command files. Fragile with relative paths across projects.
3. **Drop commands, use skills only** – Claude Code was already merging commands and skills conceptually.

Option 3 won, but it raised a new question: with separate skills per phase, how do you share methodology knowledge (rules, concepts, directory structure) without duplicating it everywhere?

The answer came from studying openspec, which generates its skills from templates. Instead of duplicating knowledge across skill files, a CLI tool composes shared partials with phase-specific content to produce self-contained skills. The generation is the deduplication mechanism.

This led to the architecture split:

- **spexl the CLI** – owns the methodology. Plumbing (file management), generation (compose skills for agents), and runtime steering (serve knowledge on demand).
- **Generated skills** – thin orchestration layers that call back into spexl for context and templates. Self-contained when loaded, but deduplicated at authoring time.

The name changed from `spectl` to `spexl` to reflect the broader scope – it's no longer just a "spec control" utility but a complete spec-driven development tool.

## Lineage

The prior `spec-driven-dev` plugin continues to exist in `my-claude-plugins` for backward compatibility. Archived changes from that era are preserved in `docs/historical/`. The reference specs for spectl and spec-sync were carried forward as starting points.
