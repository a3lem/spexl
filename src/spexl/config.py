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
    agents: dict[str, dict[str, str]] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: Path) -> ProjectConfig:
        """Parse a .spexl.toml file, applying defaults for missing fields."""
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

        agents: dict[str, dict[str, str]] = {}
        raw_agents: dict[str, dict[str, T.Any]] = data.get("agents", {})
        for agent_name, agent_conf in raw_agents.items():
            assert isinstance(agent_conf, dict), (
                f"agents.{agent_name} must be a table, got {type(agent_conf).__name__}"
            )
            agents[agent_name] = {k: str(v) for k, v in agent_conf.items()}

        return cls(
            toml_path=path,
            specs_location=specs_location,
            agents=agents,
        )

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

    @property
    def has_install_path(self) -> bool:
        return any("install_path" in conf for conf in self.agents.values())


def find_nearest_config(start: Path | None = None) -> ProjectConfig:
    """Walk up from start to find the nearest .spexl.toml.

    Raises SpexlError if none found before hitting the filesystem root.
    """
    result = _walk_up(start or Path.cwd())
    if result is None:
        raise SpexlError(
            f"No {CONFIG_FILENAME} found. Run 'spexl init' to initialize."
        )
    return result


def find_project_root(start: Path | None = None) -> ProjectConfig:
    """Walk up from start to find the project root .spexl.toml.

    The project root is the first .spexl.toml with an install_path,
    or the topmost .spexl.toml before a .git boundary.
    """
    current = (start or Path.cwd()).resolve()
    topmost: ProjectConfig | None = None

    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            config = ProjectConfig.from_toml(candidate)
            topmost = config
            if config.has_install_path:
                return config

        # Stop at .git boundary
        if (current / ".git").exists():
            break

        parent = current.parent
        if parent == current:
            break
        current = parent

    if topmost is not None:
        return topmost

    raise SpexlError(
        f"No {CONFIG_FILENAME} found. Run 'spexl init' to initialize."
    )


def discover_all_configs(start: Path | None = None) -> list[ProjectConfig]:
    """Walk DOWN from start to find all .spexl.toml files.

    Spec discovery only looks below you, never above. This means running
    from a subdir without specs shows nothing – not the parent's specs.
    """
    base = start or Path.cwd()
    return _walk_down(base)


def discover_single_config(start: Path | None = None) -> ProjectConfig:
    """Find the nearest .spexl.toml without walking down (--no-recurse mode)."""
    return find_nearest_config(start)


def _walk_up(start: Path) -> ProjectConfig | None:
    """Walk up from start looking for .spexl.toml. Returns None if not found."""
    current = start.resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return ProjectConfig.from_toml(candidate)

        # Stop at .git boundary
        if (current / ".git").exists():
            return None

        parent = current.parent
        if parent == current:
            return None
        current = parent


def _walk_down(root: Path) -> list[ProjectConfig]:
    """Walk down from root to find all .spexl.toml files, skipping noise dirs."""
    configs: list[ProjectConfig] = []
    _walk_down_recursive(root, configs)
    return sorted(configs, key=lambda c: c.toml_path)


def _walk_down_recursive(directory: Path, configs: list[ProjectConfig]) -> None:
    """Recursively walk directory tree collecting .spexl.toml configs."""
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
    """Read and parse .spexl.toml."""
    with open(path, "rb") as f:
        return tomllib.load(f)


def write_config(
    path: Path,
    agents: dict[str, str] | None = None,
    specs_location: SpecsLocation | None = None,
) -> None:
    """Write a .spexl.toml with the given sections.

    agents: {target_name: install_path_str}
    specs_location: SpecsLocation with non-default values to write
    """
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

    if agents:
        for target_name, install_path_str in agents.items():
            lines.append(f"[agents.{target_name}]")
            normalized = install_path_str.rstrip("/") + "/"
            lines.append(f'install_path = "{normalized}"')
            lines.append("")

    path.write_text("\n".join(lines) if lines else "")


def update_config(
    config_path: Path,
    target: str,
    install_path_str: str,
) -> None:
    """Add or update a target in an existing .spexl.toml.

    Re-reads the config, updates the agents section, and rewrites.
    """
    config = read_config(config_path) if config_path.stat().st_size > 0 else {}
    if "agents" not in config:
        config["agents"] = {}
    config["agents"][target] = {"install_path": install_path_str}

    agents = {name: cfg["install_path"] for name, cfg in config["agents"].items()}

    # Preserve specs_location if present
    raw_loc = config.get("specs_location", {})
    specs_loc = None
    if raw_loc:
        specs_loc = SpecsLocation(
            dir_path=raw_loc.get("dir_path", "./specs"),
            changes_dir=raw_loc.get("changes_dir", "changes"),
            reference_dir=raw_loc.get("reference_dir", "reference"),
        )

    write_config(config_path, agents=agents, specs_location=specs_loc)
