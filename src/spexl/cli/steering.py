# [AI]
# Context: drop-composition change -- replace prime/explain/template with a single onboard command
# Intent: print the onboard primer (for manual paste into AGENTS.md/CLAUDE.md) with guidance to stderr
# Assumes: onboard content lives at spexl.content.onboard.md; deeper methodology is served by the
#          spexl-foundations skill rather than by a CLI command

import argparse
import importlib.resources
import sys
import typing as T


def register(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    p_onboard = subparsers.add_parser(
        "onboard",
        help="Print the primer to paste into AGENTS.md or CLAUDE.md",
    )
    p_onboard.set_defaults(func=cmd_onboard)


def cmd_onboard(_args: T.Any) -> None:
    content = importlib.resources.files("spexl.content").joinpath("onboard.md").read_text(
        encoding="utf-8"
    )
    # [AI]
    # Context: drop-composition change
    # Intent: header to stderr so `spexl onboard >> AGENTS.md` pipes clean content,
    #         while the interactive hint is still visible in the terminal
    header = "# Add this to your AGENTS.md or CLAUDE.md\n# (Pipe: spexl onboard >> AGENTS.md)\n"
    print(header, file=sys.stderr)
    print(content, end="")
