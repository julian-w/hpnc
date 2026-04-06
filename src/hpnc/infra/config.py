"""ConfigLoader — project root discovery and configuration loading (FR7).

Stub implementation. Full implementation in Story 2.1.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

__all__ = ["Config", "ConfigLoader"]


@dataclass
class Config:
    """HPNC project configuration from _hpnc/config.yaml.

    Args:
        project_name: Name of the project.
        project_root: Absolute path to the project root.
        merge_target: Git branch for merge operations.
        log_verbosity: Logging level — "minimal", "normal", or "verbose".
        agent_output: Agent output capture — "full", "truncated", or "none".
    """

    project_name: str
    project_root: Path
    merge_target: str = "main"
    log_verbosity: str = "normal"
    agent_output: str = "full"


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
        raise NotImplementedError("Implemented in Story 2.1")

    def load(self, root: Path) -> Config:
        """Parse config.yaml and return a Config instance.

        Args:
            root: Path to the project root directory.

        Returns:
            Parsed project configuration.

        Raises:
            ConfigError: If the config file is invalid.
        """
        raise NotImplementedError("Implemented in Story 2.1")
