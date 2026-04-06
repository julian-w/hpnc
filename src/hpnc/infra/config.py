"""ConfigLoader — project root discovery and configuration loading (FR7).

Searches upward for _hpnc/config.yaml, parses YAML, merges with defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from hpnc.infra.errors import ConfigError

__all__ = ["Config", "ConfigLoader"]

CONFIG_DIR = "_hpnc"
CONFIG_FILE = "config.yaml"

_DEFAULTS: dict[str, Any] = {
    "merge_target": "main",
    "log_verbosity": "normal",
    "agent_output": "full",
    "timeout": "30m",
    "max_fix_attempts": 3,
    "executor": "opus",
    "reviewer": "codex",
    "executor_model": "",
    "reviewer_model": "",
    "max_turns": 10,
    "protected_paths": ["_hpnc/", "_bmad/", ".claude/"],
}


@dataclass
class Config:
    """HPNC project configuration from _hpnc/config.yaml.

    Args:
        project_name: Name of the project (mandatory).
        project_root: Absolute path to the project root.
        merge_target: Git branch for merge operations.
        log_verbosity: Logging level — "minimal", "normal", or "verbose".
        agent_output: Agent output capture — "full", "truncated", or "none".
        timeout: Task timeout duration string.
        max_fix_attempts: Maximum fix-loop retry attempts.
        executor: Default executor agent identifier.
        reviewer: Default reviewer agent identifier.
        protected_paths: Paths that agents must not modify.
    """

    project_name: str
    project_root: Path
    merge_target: str = "main"
    log_verbosity: str = "normal"
    agent_output: str = "full"
    timeout: str = "30m"
    max_fix_attempts: int = 3
    executor: str = "opus"
    reviewer: str = "codex"
    executor_model: str = ""
    reviewer_model: str = ""
    max_turns: int = 10
    protected_paths: list[str] = field(
        default_factory=lambda: ["_hpnc/", "_bmad/", ".claude/"]
    )


class ConfigLoader:
    """Loads and validates HPNC project configuration."""

    def find_root(self, start: Path | None = None) -> Path:
        """Search upward for _hpnc/config.yaml to find the project root.

        Args:
            start: Directory to start searching from. Defaults to cwd.

        Returns:
            Path to the project root directory.

        Raises:
            ConfigError: If no _hpnc/config.yaml is found.
        """
        current = (start or Path.cwd()).resolve()

        while True:
            config_path = current / CONFIG_DIR / CONFIG_FILE
            if config_path.is_file():
                return current
            parent = current.parent
            if parent == current:
                raise ConfigError(
                    what="HPNC project not found",
                    why=f"No {CONFIG_DIR}/{CONFIG_FILE} found in any parent directory",
                    action="Run 'hpnc init' to initialize HPNC in your project",
                )
            current = parent

    def load(self, root: Path) -> Config:
        """Parse config.yaml and return a Config instance.

        Merges file values with built-in defaults. Missing optional fields
        use defaults, missing mandatory fields raise ConfigError.

        Args:
            root: Path to the project root directory.

        Returns:
            Parsed project configuration.

        Raises:
            ConfigError: If the config file is invalid or missing mandatory fields.
        """
        config_path = root / CONFIG_DIR / CONFIG_FILE
        if not config_path.is_file():
            raise ConfigError(
                what=f"Config file not found: {config_path}",
                why="The _hpnc/config.yaml file does not exist",
                action="Run 'hpnc init' to create the configuration",
            )

        try:
            with config_path.open(encoding="utf-8") as f:
                raw = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigError(
                what=f"Failed to parse config: {config_path}",
                why=str(e),
                action="Fix the YAML syntax in _hpnc/config.yaml",
            ) from e

        if not isinstance(raw, dict):
            raise ConfigError(
                what="Invalid config format",
                why=f"Expected YAML mapping, got {type(raw).__name__}",
                action="Ensure _hpnc/config.yaml contains key-value pairs",
            )

        if "project_name" not in raw:
            raise ConfigError(
                what="Missing mandatory field: project_name",
                why="project_name is required in _hpnc/config.yaml",
                action="Add 'project_name: your-project' to _hpnc/config.yaml",
            )

        merged = {**_DEFAULTS, **raw}

        # Merge list fields (union) instead of replace
        default_paths = set(_DEFAULTS.get("protected_paths", []))
        user_paths = set(raw.get("protected_paths", []))
        merged["protected_paths"] = sorted(default_paths | user_paths)

        return Config(
            project_name=merged["project_name"],
            project_root=root.resolve(),
            merge_target=merged["merge_target"],
            log_verbosity=merged["log_verbosity"],
            agent_output=merged["agent_output"],
            timeout=merged["timeout"],
            max_fix_attempts=merged["max_fix_attempts"],
            executor=merged["executor"],
            reviewer=merged["reviewer"],
            executor_model=merged["executor_model"],
            reviewer_model=merged["reviewer_model"],
            max_turns=merged["max_turns"],
            protected_paths=merged["protected_paths"],
        )
