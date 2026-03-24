# [AI]
# Context: replace-context-with-prime-and-explain
# Intent: three-level knowledge delivery – prime (foundational), explain (advanced), template (scaffolding)
# Assumes: templates package has prime/, partials/, concepts/, and artifacts/ categories

import argparse
import sys
import typing as T

from spexl.templates import read_template


# Explain registry: Level 3 topics – advanced/niche knowledge, on demand.
EXPLAIN_REGISTRY: dict[str, dict[str, T.Any]] = {
    "spexl": {
        "description": "Full SDD methodology overview (concepts, glossary, workflow)",
        "sources": [("concepts", "concepts.md")],
    },
    "spec-notation": {
        "description": "Notation and structure guidance for writing spec deltas",
        "sources": [("partials", "spec.md")],
    },
    "design": {
        "description": "Guidance for writing design documents",
        "sources": [("partials", "design.md")],
    },
    "tasks": {
        "description": "Guidance for writing task breakdowns",
        "sources": [("partials", "tasks.md")],
    },
    "verification": {
        "description": "Test strategies and annotation conventions",
        "sources": [("partials", "verification.md")],
    },
    "critique": {
        "description": "Spec-critic checklists and modes",
        "sources": [("partials", "critique.md")],
    },
}

# Artifact template registry: maps type names to template files.
ARTIFACT_REGISTRY: dict[str, dict[str, str]] = {
    "proposal": {
        "description": "Proposal template (why, what changes, capabilities, impact)",
        "file": "proposal.md",
    },
    "spec-delta": {
        "description": "Spec delta template (ADDED/MODIFIED/REMOVED requirements)",
        "file": "spec-delta.md",
    },
    "reference-spec": {
        "description": "Reference spec template (overview, requirements, scenarios)",
        "file": "reference-spec.md",
    },
    "design": {
        "description": "Design document template (context, decisions, risks)",
        "file": "design.md",
    },
    "tasks": {
        "description": "Task breakdown template (checkboxes, phases)",
        "file": "tasks.md",
    },
}


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_prime = subparsers.add_parser(
        "prime", help="Print foundational spexl knowledge for system prompt injection"
    )
    p_prime.set_defaults(func=cmd_prime)

    p_explain = subparsers.add_parser(
        "explain", help="Print advanced/niche knowledge on demand"
    )
    p_explain.add_argument(
        "topic",
        nargs="?",
        help="Topic name (e.g. spec-notation, verification, critique)",
    )
    p_explain.add_argument(
        "--list",
        action="store_true",
        dest="list_topics",
        help="List available topics",
    )
    p_explain.set_defaults(func=cmd_explain)

    p_template = subparsers.add_parser(
        "template", help="Print an artifact template to stdout"
    )
    p_template.add_argument(
        "artifact_type",
        nargs="?",
        help="Artifact type (e.g. proposal, spec-delta, design, tasks)",
    )
    p_template.add_argument(
        "--list",
        action="store_true",
        dest="list_types",
        help="List available artifact types",
    )
    p_template.set_defaults(func=cmd_template)


def cmd_prime(_args: T.Any) -> None:
    content = read_template("prime", "prime.md")
    print(content, end="")


def cmd_explain(args: T.Any) -> None:
    if args.list_topics:
        for name, info in sorted(EXPLAIN_REGISTRY.items()):
            print(f"  {name:20s} {info['description']}")
        return

    if not args.topic:
        print("error: topic required. Use --list to see available topics.", file=sys.stderr)
        sys.exit(1)

    topic = args.topic
    if topic not in EXPLAIN_REGISTRY:
        valid = ", ".join(sorted(EXPLAIN_REGISTRY))
        print(f"error: unknown topic '{topic}'. Valid topics: {valid}", file=sys.stderr)
        sys.exit(1)

    parts: list[str] = []
    for category, name in EXPLAIN_REGISTRY[topic]["sources"]:
        content = read_template(category, name)
        parts.append(content.strip())

    print("\n\n---\n\n".join(parts))


def cmd_template(args: T.Any) -> None:
    if args.list_types:
        for name, info in sorted(ARTIFACT_REGISTRY.items()):
            print(f"  {name:20s} {info['description']}")
        return

    if not args.artifact_type:
        print("error: artifact type required. Use --list to see available types.", file=sys.stderr)
        sys.exit(1)

    artifact_type = args.artifact_type
    if artifact_type not in ARTIFACT_REGISTRY:
        valid = ", ".join(sorted(ARTIFACT_REGISTRY))
        print(f"error: unknown artifact type '{artifact_type}'. Valid types: {valid}", file=sys.stderr)
        sys.exit(1)

    content = read_template("artifacts", ARTIFACT_REGISTRY[artifact_type]["file"])
    print(content, end="")
