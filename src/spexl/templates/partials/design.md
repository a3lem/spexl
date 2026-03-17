# Design Phase Reference

The proposal says *why*, specs say *what*, design says *how*. A design doc covers the technical approach: decisions, code organization, data flow, error handling -- everything needed to start coding without guessing.

## Mode Detection

- If `design.md` doesn't exist → **Create mode**
- If `design.md` exists → **Refine mode** (update based on instruction)

## When to Include

Create design.md only if any of these apply:
- Change touches multiple services/modules, or introduces a new pattern
- New external dependency or significant data model changes
- Security, performance, or migration complexity
- Ambiguity that benefits from technical decisions before coding

Skip for simple features, bug fixes, or obvious implementations.

## Process

### 1. Load Context

Read the spec's `proposal.md` and `deltas/*/spec.md` to understand:
- Problem being solved and motivation
- Scenarios to satisfy
- Constraints to respect

If refining, also read existing `design.md`.

### 2. Explore Approach

In **Create mode**: Use AskUserQuestion to explore:
- High-level implementation strategy
- Key architectural choices
- Trade-offs between approaches

In **Refine mode**: Apply the user's instruction to existing design.

**Capturing research:** If exploration yields insights too incidental for design.md (e.g., explored files, rejected approaches, useful links), record them in `notes/research.md`.

### 3. Write design.md

Use template from `templates/design.md`.

Sections:
- **Context** -- Background, current state, constraints
- **Goals / Non-Goals** -- What this design achieves and explicitly excludes
- **Decisions** -- Implementation choices with rationale. Each decision should give an implementer enough to code against without further discussion. Include alternatives considered.
- **Risks / Trade-offs** -- Known limitations, format: `[Risk] → Mitigation`
- **Open Questions** -- Outstanding decisions or unknowns. Remove when all resolved.

Examples of what a decision might cover: code organization and module structure, command/API dispatch patterns, data flow through the system, interfaces and contracts, data models and storage, error handling and reporting strategy, output formatting, configuration and discovery logic, migration/rollback strategy.

These belong in the Decisions section with rationale -- not as separate top-level sections.

The design is complete when someone could implement the spec without making architectural choices on the fly. If a decision will need to be made during coding, it should be made here first.

### 4. Warn if Design Changes Break Implementation (Refine mode only)

If design changed significantly, warn user that implementation may need adjusting.
