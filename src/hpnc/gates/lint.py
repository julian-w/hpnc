"""Lint verification gate (FR55).

Executes the project's lint command and returns pass/fail.
Pass only when subprocess exit code is 0 (NFR7).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from hpnc.constants import GATE_TIMEOUT
from hpnc.gates.runner import GateResult

__all__ = ["LintGate"]

_DEFAULT_COMMAND: list[str] = ["uv", "run", "ruff", "check", "."]


class LintGate:
    """Verifies that the project passes lint checks.

    Args:
        command: Lint command to execute. Defaults to ruff via uv.
    """

    def __init__(self, command: list[str] | None = None) -> None:
        self._command = command if command is not None else _DEFAULT_COMMAND

    @property
    def name(self) -> str:
        """Gate identifier."""
        return "lint"

    def run(self, worktree: Path) -> GateResult:
        """Execute the lint command in the worktree.

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
                timeout=GATE_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return GateResult(
                name=self.name,
                passed=False,
                exit_code=-1,
                stderr=f"Gate timed out after {GATE_TIMEOUT}s",
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
