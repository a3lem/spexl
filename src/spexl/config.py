# [AI]
# Context: spex-9c9a (shablon migration); install_targets removed -- agent assets
#          are distributed via the Claude Code plugin, not the CLI.
# Intent: minimal project config -- .spexl.toml records [specs_location] only.

from __future__ import annotations

import tomllib
import typing as T
from dataclasses import dataclass, field
from pathlib import Path

from spexl.errors import SpexlError

CONFIG_FILENAME = ".spexl.toml"

SKIP_DIRS = frozenset({"node_modules", ".venv", ".git", "__pycache__", "archive"})


@dataclass
class SpecsLocation:
    dir_path: str = "./specs"
    changes_dir: str = "changes"
    reference_dir: str = "reference"


@dataclass
class ProjectConfig:
    toml_path: Path
    specs_location: SpecsLocation = field(default_factory=SpecsLocation)

    @classmethod
    def from_toml(cls, path: Path) -> ProjectConfig:
        if path.stat().st_size == 0:
            return cls(toml_path=path)

        with open(path, "rb") as f:
            data: dict[str, T.Any] = tomllib.load(f)

        raw_loc: dict[str, str] = data.get("specs_location", {})
        specs_location = SpecsLocation(
            dir_path=raw_loc.get("dir_path", "./specs"),
            changes_dir=raw_loc.get("changes_dir", "changes"),
            reference_dir=raw_loc.get("reference_dir", "reference"),
        )

        return cls(toml_path=path, specs_location=specs_location)

    @property
    def project_dir(self) -> Path:
        return self.toml_path.parent

    @property
    def specs_dir(self) -> Path:
        return self.project_dir / self.specs_location.dir_path

    @property
    def changes_path(self) -> Path:
        return self.specs_dir / self.specs_location.changes_dir

    @property
    def reference_path(self) -> Path:
        return self.specs_dir / self.specs_location.reference_dir


def find_nearest_config(start: Path | None = None) -> ProjectConfig:
    result = _walk_up(start or Path.cwd())
    if result is None:
        raise SpexlError(
            f"No {CONFIG_FILENAME} found. Run 'spexl init' to initialize."
        )
    return result


def discover_all_configs(start: Path | None = None) -> list[ProjectConfig]:
    base = start or Path.cwd()
    return _walk_down(base)


def discover_single_config(start: Path | None = None) -> ProjectConfig:
    return find_nearest_config(start)


def _walk_up(start: Path) -> ProjectConfig | None:
    current = start.resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return ProjectConfig.from_toml(candidate)

        if (current / ".git").exists():
            return None

        parent = current.parent
        if parent == current:
            return None
        current = parent


def _walk_down(root: Path) -> list[ProjectConfig]:
    configs: list[ProjectConfig] = []
    _walk_down_recursive(root, configs)
    return sorted(configs, key=lambda c: c.toml_path)


def _walk_down_recursive(directory: Path, configs: list[ProjectConfig]) -> None:
    try:
        entries = sorted(directory.iterdir())
    except PermissionError:
        return

    for entry in entries:
        if entry.is_file() and entry.name == CONFIG_FILENAME:
            configs.append(ProjectConfig.from_toml(entry))
        elif entry.is_dir() and entry.name not in SKIP_DIRS:
            _walk_down_recursive(entry, configs)


# -- Config file I/O --


def read_config(path: Path) -> dict[str, T.Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def write_config(
    path: Path,
    specs_location: SpecsLocation | None = None,
) -> None:
    lines: list[str] = []

    if specs_location is not None:
        defaults = SpecsLocation()
        loc_lines: list[str] = []
        if specs_location.dir_path != defaults.dir_path:
            loc_lines.append(f'dir_path = "{specs_location.dir_path}"')
        if specs_location.changes_dir != defaults.changes_dir:
            loc_lines.append(f'changes_dir = "{specs_location.changes_dir}"')
        if specs_location.reference_dir != defaults.reference_dir:
            loc_lines.append(f'reference_dir = "{specs_location.reference_dir}"')
        if loc_lines:
            lines.append("[specs_location]")
            lines.extend(loc_lines)
            lines.append("")

    path.write_text("\n".join(lines) if lines else "")
