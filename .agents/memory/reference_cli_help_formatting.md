---
name: reference_cli_help_formatting
description: How spexl's CLI help is customized - _Formatter and _Parser subclasses in __init__.py
type: reference
---

spexl customizes argparse help output in `src/spexl/__init__.py` with two classes:

**`_Formatter(argparse.HelpFormatter)`** – Overrides `_format_action` to suppress the auto-generated `{cmd1,cmd2,...}` metavar line for subparsers. Instead of rendering the parent `_SubParsersAction` (which produces the metavar), it directly renders the child `_ChoicesPseudoAction` entries with an extra indent level via `self._indent()` / `self._dedent()`.

**`_Parser(argparse.ArgumentParser)`** – Overrides `format_help` to reorder sections: description, usage, commands, options (argparse default is usage, description, options, commands). Iterates `self._action_groups` by title in the desired order.

Other details:
- `title="commands"` on `add_subparsers` renames the section header
- Custom `usage=` string avoids the `{cmd1,...} ...` noise in the usage line
- Each CLI module's `register()` function is unchanged; it still calls `subparsers.add_parser(name, help=...)` normally
