# [AI]
# Context: rewrite-as-spexl (task 5.1)
# Intent: compose partials + action templates into self-contained SKILL.md files
# Assumes: all partials and actions exist in templates package

import importlib.metadata
import typing as T
from datetime import date

from spexl.templates import read_template


SKILL_MANIFESTS: dict[str, dict[str, T.Any]] = {
    "explore": {
        "description": (
            'This skill should be used when the user asks to "explore an idea", '
            '"investigate a problem", "think through requirements", "research before proposing", '
            'or wants to explore ideas before committing to a formal spec change.'
        ),
        "partials": ["rules"],
        "action": "explore",
    },
    "propose": {
        "description": (
            'This skill should be used when the user asks to "propose a change", '
            '"create a spec", "start a new feature", "define requirements", '
            'or wants to create a formal specification for a new capability or modification.'
        ),
        "partials": ["rules", "structure", "file-ownership", "cross-phase"],
        "action": "propose",
    },
    "refine": {
        "description": (
            'This skill should be used when the user asks to "refine a spec", '
            '"update the proposal", "modify the design", "change requirements", '
            'or wants to update any existing spec artifact.'
        ),
        "partials": ["rules", "file-ownership"],
        "action": "refine",
    },
    "apply": {
        "description": (
            'This skill should be used when the user asks to "implement a spec", '
            '"apply a change", "build the feature", "start implementation", '
            'or wants to implement and verify a proposed spec change.'
        ),
        "partials": ["rules", "structure", "file-ownership", "cross-phase", "interactive-vs-autonomous"],
        "action": "apply",
    },
    "archive": {
        "description": (
            'This skill should be used when the user asks to "archive a change", '
            '"merge deltas", "finalize a spec", "complete a change", '
            'or wants to merge spec deltas into reference specs and archive the change.'
        ),
        "partials": ["rules"],
        "action": "archive",
    },
}


def compose_skill(action_name: str) -> str:
    """Assemble a complete SKILL.md from the manifest for a given action."""
    assert action_name in SKILL_MANIFESTS, f"Unknown action: {action_name}"
    manifest = SKILL_MANIFESTS[action_name]

    version = importlib.metadata.version("spexl")
    today = date.today().isoformat()

    sections: list[str] = []

    # YAML frontmatter must start at byte 0
    frontmatter = "\n".join([
        "---",
        f"name: spexl-{action_name}",
        f"description: {manifest['description']}",
        "metadata:",
        f"  generated_by: spexl {version}",
        f"  generated_on: {today}",
        "---",
    ])
    sections.append(frontmatter)

    # Title
    sections.append(f"# {action_name.capitalize()}")

    # Partials
    for partial_name in manifest["partials"]:
        content = read_template("partials", f"{partial_name}.md").strip()
        sections.append(f"<!-- spexl:{partial_name} -->\n{content}")

    # Action content
    action_content = read_template("actions", f"{manifest['action']}.md").strip()
    sections.append(f"<!-- spexl:action -->\n{action_content}")

    # Steering reference section
    steering = _steering_section(action_name)
    sections.append(f"<!-- spexl:steering -->\n{steering}")

    return "\n\n".join(sections) + "\n"


def _steering_section(action_name: str) -> str:
    """Generate the runtime steering reference section."""
    lines = [
        "## Runtime Context",
        "",
        "For additional context during execution:",
        f"- `spexl context {action_name}` -- full phase-specific guidance",
        "- `spexl context rules` -- core SDD rules",
        "- `spexl context spec-notation` -- notation for writing spec deltas",
        "- `spexl template <type>` -- artifact templates (proposal, spec-delta, design, tasks)",
        "- `spexl new <slug>` -- scaffold a new change directory",
        "- `spexl validate` -- check structural integrity",
        "- `spexl changes` -- list active changes",
        "- `spexl info <slug>` -- show change overview",
    ]
    return "\n".join(lines)
