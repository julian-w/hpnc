"""Workspace — file I/O abstraction with atomic writes (NFR11).

All file operations go through this class to ensure atomic writes,
consistent path resolution, and testability via root injection.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from hpnc.infra.errors import ConfigError

__all__ = ["Workspace"]


class Workspace:
    """Abstraction for all file operations against the project root.

    In production, root points to the project directory.
    In tests, root points to a temporary directory.

    Args:
        root: The root directory for all file operations.
    """

    def __init__(self, root: Path) -> None:
        self.root = root

    def _resolve(self, path: Path) -> Path:
        """Resolve a path against the workspace root.

        Args:
            path: Absolute or relative path. Relative paths are
                resolved against self.root.

        Returns:
            The resolved absolute path.
        """
        if path.is_absolute():
            return path
        return self.root / path

    def read_yaml(self, path: Path) -> dict[str, Any]:
        """Read and parse a YAML file.

        Args:
            path: Path to the YAML file (relative or absolute).

        Returns:
            Parsed YAML content as a dictionary.

        Raises:
            ConfigError: If the file does not exist or cannot be parsed.
        """
        resolved = self._resolve(path)
        if not resolved.exists():
            raise ConfigError(
                what=f"YAML file not found: {resolved}",
                why="The file does not exist at the expected location",
                action=f"Create the file at {resolved} or check the path",
            )
        try:
            with resolved.open(encoding="utf-8") as f:
                result = yaml.safe_load(f)
                if result is None:
                    return {}
                if not isinstance(result, dict):
                    raise ConfigError(
                        what=f"Unexpected YAML structure in {resolved}",
                        why=f"Expected a mapping (dict), got {type(result).__name__}",
                        action="Ensure the file contains a YAML mapping (key: value pairs)",
                    )
                return result
        except yaml.YAMLError as e:
            raise ConfigError(
                what=f"Failed to parse YAML: {resolved}",
                why=str(e),
                action="Fix the YAML syntax in the file",
            ) from e

    def write_yaml_atomic(self, path: Path, data: dict[str, Any]) -> None:
        """Write data to a YAML file atomically (write-to-temp, then rename).

        Uses os.replace() for atomic rename. The temp file is created in the
        same directory to ensure same-filesystem operation.

        Args:
            path: Path to the YAML file (relative or absolute).
            data: Data to serialize and write.
        """
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(resolved.parent), suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            os.replace(tmp_path, str(resolved))
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise

    def read_markdown(self, path: Path) -> str:
        """Read a markdown file and return its content.

        Args:
            path: Path to the markdown file (relative or absolute).

        Returns:
            File content as a string.

        Raises:
            ConfigError: If the file does not exist.
        """
        resolved = self._resolve(path)
        if not resolved.exists():
            raise ConfigError(
                what=f"Markdown file not found: {resolved}",
                why="The file does not exist at the expected location",
                action=f"Create the file at {resolved} or check the path",
            )
        return resolved.read_text(encoding="utf-8")
