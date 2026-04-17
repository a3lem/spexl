# Design Guidance

The proposal says *why*, specs say *what*, design says *how*. A design doc covers the technical approach: decisions, code organization, data flow, error handling -- everything needed to start coding without guessing.

## When to Include

Create `design.md` only if any of these apply:

- Change touches multiple services/modules, or introduces a new pattern
- New external dependency or significant data model changes
- Security, performance, or migration complexity
- Ambiguity that benefits from technical decisions before coding

Skip for simple features, bug fixes, or obvious implementations.

## Sections

- **Context** -- Background, current state, constraints
- **Goals / Non-Goals** -- What this design achieves and explicitly excludes
- **Decisions** -- Implementation choices with rationale. Each decision should give an implementer enough to code against without further discussion. Include alternatives considered.
- **Risks / Trade-offs** -- Known limitations, format: `[Risk] → Mitigation`
- **Open Questions** -- Outstanding decisions or unknowns. Remove when all resolved.

Examples of what a decision might cover: code organization and module structure, command/API dispatch patterns, data flow through the system, interfaces and contracts, data models and storage, error handling and reporting strategy, output formatting, configuration and discovery logic, migration/rollback strategy.

These belong in the Decisions section with rationale -- not as separate top-level sections.

## Completeness Criterion

The design is complete when someone could implement the spec without making architectural choices on the fly. If a decision will need to be made during coding, it should be made here first.

## Template

```markdown
## Context

## Goals / Non-Goals

## Decisions

### [Decision title]

**Alternatives considered:**

## Risks / Trade-offs / Limitations

## Open Questions
```

## Capturing Research

If exploration yields insights too incidental for `design.md` (e.g., explored files, rejected approaches, useful links), record them in `notes/research.md`.

## Cascading Effects

If the design changes significantly during refine, warn the user that implementation may need adjusting. If a spec changes after the design exists, warn that the design may be stale.
