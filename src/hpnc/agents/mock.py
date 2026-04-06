"""Configurable mock agent executor for token-free testing (FR74).

Returns real subprocess.Popen objects to satisfy the AgentExecutor Protocol
while providing full control over exit status, delay, and simulated file changes.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from hpnc.agents.base import ExitStatus

if TYPE_CHECKING:
    from hpnc.infra.config import Config

__all__ = ["MockAgentExecutor"]

EXIT_CODE_MAP: dict[ExitStatus, int] = {
    ExitStatus.SUCCESS: 0,
    ExitStatus.FAILURE: 1,
    ExitStatus.TIMEOUT: 2,
}
"""Maps ExitStatus to subprocess exit codes."""


class MockAgentExecutor:
    """Mock implementation of AgentExecutor for testing and --mock mode.

    Args:
        default_status: The exit status to simulate.
        delay: Seconds to sleep before exiting (simulates agent work time).
        file_changes: List of filenames to create in the story's parent directory.
    """

    def __init__(
        self,
        default_status: ExitStatus = ExitStatus.SUCCESS,
        delay: float = 0.0,
        file_changes: list[str] | None = None,
    ) -> None:
        self.default_status = default_status
        self.delay = delay
        self.file_changes = file_changes or []

    def start(
        self,
        story: Path,
        config: Config,
        instructions: Path,
    ) -> subprocess.Popen[str]:
        """Start a mock agent process.

        Writes simulated file changes to the story's parent directory,
        then launches a trivial Python subprocess that exits with the
        configured exit code after the configured delay.

        Args:
            story: Path to the story markdown file.
            config: Project configuration (unused by mock).
            instructions: Path to executor instructions file (unused by mock).

        Returns:
            A running subprocess that will exit with the configured status.
        """
        worktree = story.parent
        for filename in self.file_changes:
            filepath = worktree / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(f"# Mock generated: {filename}\n")

        exit_code = EXIT_CODE_MAP[self.default_status]

        return subprocess.Popen(
            [
                sys.executable,
                "-c",
                f"import time, sys; time.sleep({self.delay}); "
                f"print('[mock] Processing story...'); "
                f"print('[mock] Done.'); "
                f"sys.exit({exit_code})",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def stream_output(
        self, process: subprocess.Popen[str]
    ) -> Iterator[str]:
        """Stream output lines from the mock process.

        Args:
            process: The running mock subprocess.

        Yields:
            Output lines from the mock agent.
        """
        if process.stdout is not None:
            for line in process.stdout:
                yield line.rstrip("\n")

    def get_exit_status(
        self, process: subprocess.Popen[str]
    ) -> ExitStatus:
        """Get exit status after the mock process completes.

        Args:
            process: The completed mock subprocess.

        Returns:
            The configured exit status mapped from the process exit code.
        """
        process.wait()
        code = process.returncode
        if code == 0:
            return ExitStatus.SUCCESS
        if code == 1:
            return ExitStatus.FAILURE
        return ExitStatus.TIMEOUT
