---
name: spexl-foundations
description: Foundational knowledge for spec-driven development with spexl. Load when the user asks "what is spec-driven development", "how do I use spexl", "what is a spec delta", "explain SDD", or any question about the workflow, concepts, rules, or artifacts. Action skills (spexl-propose, spexl-explore, spexl-refine, spexl-apply, spexl-archive) also tell the caller to load this skill -- it holds the concepts and references they defer to.
---

# Spexl Foundations

Spexl is two things: a **methodology** for spec-driven development, and a **CLI** that scaffolds, validates, and archives the artifacts that methodology produces. The skills installed alongside this one -- `spexl-explore`, `spexl-propose`, `spexl-refine`, `spexl-apply`, `spexl-archive` -- orchestrate the workflow. This skill holds the concepts, rules, and reference material they defer to.

## What Is a Specification?

A software specification describes what the system **must do**, in terms a reader (or a test) can verify. Not "what the code currently does" -- that is documentation. Not "how it is built" -- that is design. A spec is a contract: if the code fails to satisfy it, the code is wrong.

Good specs are concrete. Each requirement has a name, a SHALL statement expressing the rule, and scenarios showing observable inputs and outputs. Spexl uses EARS qualifiers for SHALL statements and Given/When/Then for scenarios, but the notation is secondary to the principle:

> **Specs are the source of truth. Code serves specs.**

## What Is a Spec Delta?

A specification that lags behind the code it governs is worse than none -- it actively misleads. Spexl keeps spec and code in sync with a single mechanism: **spec deltas**.

Reference specs (`specs/reference/<capability>/spec.md`) describe the system as it is now. When you change the system, you do not edit a reference spec directly. You create a **change** under `specs/changes/<slug>/` and write a **spec delta** at `deltas/<capability>/spec.md` that declares, per capability, what is:

- `ADDED` -- new requirements
- `MODIFIED` -- requirements whose behavior changes
- `REMOVED` -- requirements being retired (with reason and migration)
- `RENAMED` -- requirements whose name changes (no behavior change)

The delta expresses intent against a known baseline. You then implement the change and verify every requirement and scenario. When the work is done, the change is archived: its deltas merge into the reference specs, and the change directory moves to `changes/archive/<date>-<slug>/`. The next change builds on the updated reference.

This cycle -- **propose delta → apply → archive & merge** -- is how specs stay current as the code evolves. No delta, no change. No merge, no record.

## The Five Phases

Work moves through five phases, each a dedicated skill:

| Phase | Skill | What happens |
|-------|-------|--------------|
| Explore | `spexl-explore` | Investigate before committing. Read code, ask questions, draw diagrams. No implementation. |
| Propose | `spexl-propose` | Create a change: proposal → spec deltas → design (optional) → tasks (optional). |
| Refine | `spexl-refine` | Update any existing artifact. |
| Apply | `spexl-apply` | Implement the change. Verify against every requirement and scenario. |
| Archive | `spexl-archive` | Merge deltas into reference specs. Move the change to `changes/archive/`. |

Phases can be revisited. A snag during apply may reveal a spec gap; changing a spec may invalidate the design.

## The CLI

Run `spexl --help` for the full list. Key commands:

| Command | Purpose |
|---------|---------|
| `spexl new <slug>` | Scaffold a new change directory |
| `spexl changes` | List active changes |
| `spexl info <slug>` | Show change overview |
| `spexl refs` | List reference specs |
| `spexl validate` | Check changes for structural problems |
| `spexl archive <slug>` | Archive a completed change |

Project scaffolding (`.spexl.toml` + `specs/`) lives under `spexl init`; agent-asset setup lives under `spexl install <target>` (initial target: `claude`).

## Agents

Two sub-agents support the workflow:

- **spexl-spec-critic** -- Adversarial review. Modes: `intra-spec`, `spec-code`, `inter-spec`, `all`. Verdicts: `approved`, `approved-with-reservations`, `needs-work`, `blocked`. See `references/critique.md`.
- **spexl-spec-sync** -- Merges deltas into reference specs during archive. Handles ADDED, MODIFIED, REMOVED, RENAMED operations.

## References

Depth lives under `references/`. Load on demand based on the phase you are in. **Always read `references/rules.md` first.**

| File | When to read |
|------|--------------|
| `references/rules.md` | Always first. Core rules and anti-patterns. |
| `references/concepts.md` | Extended walkthrough of specs, capabilities, changes, artifacts, deltas, archive cycle. |
| `references/structure.md` | Directory layout and file ownership. |
| `references/spec-notation.md` | SHALL/EARS patterns, Given/When/Then scenarios, delta sections, validation checklist. |
| `references/design-guidance.md` | When and how to write `design.md`. |
| `references/tasks-guidance.md` | What belongs in `tasks.md`. |
| `references/verification.md` | Test strategies, spec annotation conventions, coverage check. |
| `references/critique.md` | `spexl-spec-critic` checklists and dialogue rules. |
| `references/modes.md` | Interactive vs autonomous behavior. |

## Usage From Action Skills

Action skills load this skill before doing anything else. They name the phase (propose, explore, refine, apply, archive) and let this skill decide which references to read. Always start with `references/rules.md`, then load whichever references fit the phase.
