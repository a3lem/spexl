#!/usr/bin/env python3
# [AI]
# Context: spex-9c9a (shablon migration)
# Intent: provide render context for .shablon/templates -- spexl version + CLI help text.

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import tomllib

root = pathlib.Path(os.environ["SHABLON_PROJECT_ROOT"])
pyproject = tomllib.loads((root / "pyproject.toml").read_text())
help_text = subprocess.run(
    ["uv", "run", "spexl", "--help"], capture_output=True, text=True, check=True
).stdout

print(
    json.dumps(
        {
            "version": pyproject["project"]["version"],
            "help_text": help_text,
        }
    )
)
