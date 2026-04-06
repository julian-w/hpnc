"""Codex CLI executor — invokes Codex for implementation/review.

All CLI-specific behavior is isolated here (NFR26).
Agent credentials are never logged or stored (NFR20).
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from hpnc.agents.base import ExitStatus
from hpnc.infra.errors import ConnectivityError

if TYPE_CHECKING:
    from hpnc.infra.config import Config

__all__ = ["CodexExecutor"]


class CodexExecutor:
    """Executes tasks via Codex CLI (FR69-FR73).

    Launches Codex as a subprocess in the task's worktree.
    Maps Codex exit codes to ExitStatus.
    """

    @staticmethod
    def check_connectivity() -> None:
        """Verify Codex CLI is installed and reachable (FR3).

        Raises:
            ConnectivityError: If Codex is not found or not responding.
        """
        try:
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise ConnectivityError(
                    what="Codex CLI not responding",
                    why=result.stderr.strip() or f"Exit code {result.returncode}",
                    action="Verify Codex is installed and authenticated",
                )
        except FileNotFoundError as e:
            raise ConnectivityError(
                what="Codex CLI not found",
                why="'codex' command not found on PATH",
                action="Install Codex: https://openai.com/codex",
            ) from e

    def start(
        self,
        story: Path,
        config: Config,
        instructions: Path,
    ) -> subprocess.Popen[str]:
        """Start Codex with the story file in the worktree.

        Args:
            story: Path to the story markdown file.
            config: Project configuration.
            instructions: Path to executor instructions file.

        Returns:
            Running Codex subprocess.
        """
        worktree = story.parent

        cmd = [
            "codex",
            "--quiet",
        ]
        if instructions.exists():
            cmd.extend(["--instructions", str(instructions)])
        cmd.extend(["--", str(story)])

        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(worktree),
        )

    def stream_output(
        self, process: subprocess.Popen[str]
    ) -> Iterator[str]:
        """Stream output lines from Codex (FR70).

        Args:
            process: The running Codex subprocess.

        Yields:
            Output lines.
        """
        if process.stdout is not None:
            for line in process.stdout:
                yield line.rstrip("\n")

    def get_exit_status(
        self, process: subprocess.Popen[str]
    ) -> ExitStatus:
        """Map Codex exit code to ExitStatus (FR71).

        Args:
            process: The completed Codex subprocess.

        Returns:
            ExitStatus based on exit code.
        """
        process.wait()
        code = process.returncode
        if code == 0:
            return ExitStatus.SUCCESS
        if code == 1:
            return ExitStatus.FAILURE
        return ExitStatus.TIMEOUT
