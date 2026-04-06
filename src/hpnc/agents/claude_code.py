"""Claude Code CLI executor — invokes Claude Code for implementation/review.

All CLI-specific behavior is isolated here (NFR26).
Agent credentials are never logged or stored (NFR20).

CLI reference: claude --bare -p "prompt" --output-format text
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

__all__ = ["ClaudeCodeExecutor"]


class ClaudeCodeExecutor:
    """Executes tasks via Claude Code CLI (FR69-FR73).

    Launches Claude Code in non-interactive mode (-p) within the task's worktree.
    Uses --bare to skip auto-discovery for consistent behavior across worktrees.
    """

    @staticmethod
    def check_connectivity() -> None:
        """Verify Claude Code CLI is installed and reachable (FR2).

        Raises:
            ConnectivityError: If Claude Code is not found or not responding.
        """
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise ConnectivityError(
                    what="Claude Code CLI not responding",
                    why=result.stderr.strip() or f"Exit code {result.returncode}",
                    action="Verify Claude Code is installed and authenticated",
                )
        except FileNotFoundError as e:
            raise ConnectivityError(
                what="Claude Code CLI not found",
                why="'claude' command not found on PATH",
                action="Install Claude Code: https://claude.ai/code",
            ) from e

    def start(
        self,
        story: Path,
        config: Config,
        instructions: Path,
    ) -> subprocess.Popen[str]:
        """Start Claude Code with the story content as prompt.

        Uses -p (non-interactive), --bare (no auto-discovery),
        and --append-system-prompt-file for executor instructions.

        Args:
            story: Path to the story markdown file.
            config: Project configuration.
            instructions: Path to executor instructions file.

        Returns:
            Running Claude Code subprocess.
        """
        worktree = story.parent
        prompt = story.read_text(encoding="utf-8")

        cmd = [
            "claude",
            "-p", prompt,
            "--dangerously-skip-permissions",
            "--output-format", "text",
            "--max-turns", str(config.max_turns),
            "--no-session-persistence",
        ]
        if config.executor_model:
            cmd.extend(["--model", config.executor_model])
        if instructions.exists():
            cmd.extend(["--append-system-prompt-file", str(instructions)])

        return subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(worktree),
        )

    def stream_output(
        self, process: subprocess.Popen[str]
    ) -> Iterator[str]:
        """Stream output lines from Claude Code (FR70).

        Args:
            process: The running Claude Code subprocess.

        Yields:
            Output lines.
        """
        if process.stdout is not None:
            for line in process.stdout:
                yield line.rstrip("\n")

    def get_exit_status(
        self, process: subprocess.Popen[str]
    ) -> ExitStatus:
        """Map Claude Code exit code to ExitStatus (FR71).

        Exit 0 = success, anything else = failure.

        Args:
            process: The completed Claude Code subprocess.

        Returns:
            ExitStatus based on exit code.
        """
        process.wait()
        if process.returncode == 0:
            return ExitStatus.SUCCESS
        return ExitStatus.FAILURE
