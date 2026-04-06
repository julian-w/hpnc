"""Build verification gate (FR53).

Executes the project's build command and returns pass/fail.
Pass only when subprocess exit code is 0 (NFR7).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from hpnc.gates.runner import GateResult

__all__ = ["BuildGate"]

_DEFAULT_COMMAND: list[str] = ["uv", "run", "python", "-c", "import hpnc"]


class BuildGate:
    """Verifies that the project builds successfully.

    Args:
        command: Build command to execute. Defaults to importing the package.
    """

    def __init__(self, command: list[str] | None = None) -> None:
        self._command = command if command is not None else _DEFAULT_COMMAND

    @property
    def name(self) -> str:
        """Gate identifier."""
        return "build"

    def run(self, worktree: Path) -> GateResult:
        """Execute the build command in the worktree.

        Args:
            worktree: Path to the Git worktree to verify.

        Returns:
            GateResult with pass/fail based on exit code.
        """
        try:
            result = subprocess.run(
                self._command,
                capture_output=True,
                text=True,
                cwd=str(worktree),
            )
        except FileNotFoundError:
            return GateResult(
                name=self.name,
                passed=False,
                exit_code=-1,
                stderr=f"Command not found: {self._command[0]}",
            )
        return GateResult(
            name=self.name,
            passed=result.returncode == 0,
            exit_code=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )
