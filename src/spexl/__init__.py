# [AI]
# Context: cli-help-cleanup
# Intent: clean CLI help with commands listed under a single "commands:" title

import argparse
import os
import sys
from pathlib import Path

import importlib.metadata

from spexl.cli import changes, generate, links, refs, steering, validate
from spexl.config import ProjectConfig, discover_all_configs, discover_single_config
from spexl.errors import SpexlError


# [AI]
# Context: cli-help-cleanup
# Intent: suppress the {cmd1,cmd2,...} metavar line for subparsers, reorder
#         help sections to: description, usage, commands, options
class _Formatter(argparse.HelpFormatter):
    def _format_action(self, action: argparse.Action) -> str:
        if isinstance(action, argparse._SubParsersAction):
            self._indent()
            parts = [self._format_action(child) for child in action._get_subactions()]
            self._dedent()
            return self._join_parts(parts)
        return super()._format_action(action)


class _Parser(argparse.ArgumentParser):
    def format_help(self) -> str:
        formatter = self._get_formatter()
        # 1. description
        formatter.add_text(self.description)
        # 2. usage
        formatter.add_usage(
            self.usage, self._actions, self._mutually_exclusive_groups,
        )
        # 3. commands, then options (instead of argparse default: options, commands)
        groups_by_title = {g.title: g for g in self._action_groups}
        for title in ("positional arguments", "commands", "options"):
            group = groups_by_title.get(title)
            if group:
                formatter.start_section(group.title)
                formatter.add_text(group.description)
                formatter.add_arguments(group._group_actions)
                formatter.end_section()
        formatter.add_text(self.epilog)
        return formatter.format_help()


def main() -> None:
    parser = _Parser(
        prog="spexl",
        description="CLI for spec-driven development",
        usage="spexl [-h] [--version] [--cwd PROJECT_DIR] command",
        formatter_class=_Formatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"spexl {importlib.metadata.version('spexl')}",
    )
    parser.add_argument(
        "--cwd",
        help="Start directory for .spexl.toml discovery",
        metavar="PROJECT_DIR",
    )

    subs = parser.add_subparsers(dest="command", title="commands")

    changes.register(subs)
    links.register(subs)
    validate.register(subs)
    refs.register(subs)
    steering.register(subs)
    generate.register(subs)


    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if not hasattr(args, "func"):
        print(f"error: unknown command '{args.command}'", file=sys.stderr)
        print("Run 'spexl --help' for available commands.", file=sys.stderr)
        sys.exit(1)

    # Commands that don't need spec root discovery
    no_root_commands = {
        steering.cmd_prime,
        steering.cmd_explain,
        steering.cmd_template,
        generate.cmd_init,
    }

    # Commands that handle their own discovery via args
    discovery_commands = {
        changes.cmd_changes,
        changes.cmd_info,
        changes.cmd_archive,
        links.cmd_link,
        links.cmd_unlink,
        refs.cmd_refs,
        validate.cmd_validate,
    }

    try:
        os.getcwd()
    except FileNotFoundError:
        print("error: current directory no longer exists", file=sys.stderr)
        sys.exit(1)

    start = Path(args.cwd) if getattr(args, "cwd", None) else None

    try:
        if args.func in no_root_commands:
            args.func(args)
        elif args.func in discovery_commands:
            args.func(args, start)
        else:
            config = discover_single_config(start)
            args.func(args, config)
    except SpexlError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
