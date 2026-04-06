"""AgentExecutor Protocol — interface for AI agent invocation.

All agent implementations (Claude Code, Codex, Mock) must satisfy this Protocol.
Uses structural typing (Protocol) — no inheritance required.
"""

from __future__ import annotations

import subprocess
from collections.abc import Iterator
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from hpnc.infra.config import Config

__all__ = ["ExitStatus", "AgentExecutor"]


class ExitStatus(Enum):
    """Agent execution exit status."""

    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


@runtime_checkable
class AgentExecutor(Protocol):
    """Interface for AI agent execution (FR75).

    Implementations must provide three capabilities:
    start an agent, stream its output, and retrieve exit status.
    """

    def start(
        self,
        story: Path,
        config: Config,
        instructions: Path,
    ) -> subprocess.Popen[str]:
        """Start an agent process with story context.

        Args:
            story: Path to the story markdown file.
            config: Project configuration.
            instructions: Path to executor instructions file.

        Returns:
            The running agent subprocess.
        """
        ...

    def stream_output(
        self, process: subprocess.Popen[str]
    ) -> Iterator[str]:
        """Stream output lines from the agent process.

        Args:
            process: The running agent subprocess.

        Yields:
            Output lines from the agent.
        """
        ...

    def get_exit_status(
        self, process: subprocess.Popen[str]
    ) -> ExitStatus:
        """Get the exit status after the agent process completes.

        Args:
            process: The completed agent subprocess.

        Returns:
            The agent's exit status.
        """
        ...
