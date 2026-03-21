# [AI]
# Context: rewrite-as-spexl (task 1.4)
# Intent: template access via importlib.resources for package data
# Assumes: this file doubles as __init__.py for the templates package,
#          making importlib.resources.files("spexl.templates") resolve correctly

import importlib.resources


def read_template(category: str, name: str) -> str:
    """Read a template file by category and name.

    e.g. read_template("artifacts", "proposal.md")
    """
    base = importlib.resources.files("spexl.templates")
    resource = base.joinpath(category, name)
    try:
        return resource.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError):
        available = list_templates(category)
        if not available:
            raise FileNotFoundError(
                f"Template category '{category}' not found. "
                f"Valid categories: {', '.join(_list_categories())}"
            )
        raise FileNotFoundError(
            f"Template '{name}' not found in '{category}'. "
            f"Available: {', '.join(available)}"
        )


def list_templates(category: str) -> list[str]:
    """List available template files in a category.

    e.g. list_templates("partials") -> ["rules.md", "structure.md", ...]
    """
    base = importlib.resources.files("spexl.templates")
    cat_dir = base.joinpath(category)
    try:
        return sorted(
            item.name
            for item in cat_dir.iterdir()
            if not item.name.startswith("__") and not item.is_dir()
        )
    except (FileNotFoundError, TypeError):
        raise FileNotFoundError(
            f"Template category '{category}' not found. "
            f"Valid categories: {', '.join(_list_categories())}"
        )


def _list_categories() -> list[str]:
    """List available template categories."""
    base = importlib.resources.files("spexl.templates")
    return sorted(
        item.name
        for item in base.iterdir()
        if item.is_dir() and not item.name.startswith("__")
    )
