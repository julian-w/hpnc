"""Workspace — file I/O abstraction with atomic writes (NFR11).

Stub implementation. Full implementation in Story 2.1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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

    def read_yaml(self, path: Path) -> dict[str, Any]:
        """Read and parse a YAML file.

        Args:
            path: Path to the YAML file (relative or absolute).

        Returns:
            Parsed YAML content as a dictionary.
        """
        raise NotImplementedError("Implemented in Story 2.1")

    def write_yaml_atomic(self, path: Path, data: dict[str, Any]) -> None:
        """Write data to a YAML file atomically (write-to-temp, then rename).

        Args:
            path: Path to the YAML file (relative or absolute).
            data: Data to serialize and write.
        """
        raise NotImplementedError("Implemented in Story 2.1")

    def read_markdown(self, path: Path) -> str:
        """Read a markdown file and return its content.

        Args:
            path: Path to the markdown file (relative or absolute).

        Returns:
            File content as a string.
        """
        raise NotImplementedError("Implemented in Story 2.1")
