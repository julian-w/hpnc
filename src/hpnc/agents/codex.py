"""Codex CLI executor — invokes Codex for implementation/review.

All CLI-specific behavior is isolated here (NFR26).
Agent credentials are never logged or stored (NFR20).

CLI reference: codex exec "prompt" --full-auto
Note: On Windows, Codex is a Node.js .cmd wrapper — use shutil.which() to resolve.
"""

from __future__ import annotations

import shutil
import subprocess
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from hpnc.agents.base import ExitStatus
from hpnc.infra.errors import ConnectivityError

if TYPE_CHECKING:
    from hpnc.infra.config import Config

__all__ = ["CodexExecutor"]


def _find_codex() -> str:
    """Find the codex executable, handling Windows .cmd wrappers.

    Returns:
        Full path to codex executable, or "codex" as fallback.
    """
    found = shutil.which("codex")
    return found if found else "codex"


class CodexExecutor:
    """Executes tasks via Codex CLI (FR69-FR73).

    Launches Codex in non-interactive exec mode within the task's worktree.
    Uses --full-auto for autonomous execution (workspace-write sandbox).
    """

    @staticmethod
    def check_connectivity() -> None:
        """Verify Codex CLI is installed and reachable (FR3).

        Raises:
            ConnectivityError: If Codex is not found or not responding.
        """
        try:
            result = subprocess.run(
                [_find_codex(), "--version"],
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
                action="Install Codex: npm install -g @openai/codex",
            ) from e

    @staticmethod
    def preflight_check(worktree: Path) -> None:
        """Verify Codex can authenticate, edit files, and run commands.

        Args:
            worktree: Directory to run the preflight check in (must be a git repo).

        Raises:
            ConnectivityError: If any capability check fails.
        """
        try:
            result = subprocess.run(
                [
                    _find_codex(), "exec", "--full-auto",
                    "Respond with exactly: PREFLIGHT_OK",
                ],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                cwd=str(worktree),
                timeout=60,
            )
            if result.returncode != 0:
                raise ConnectivityError(
                    what="Codex preflight failed",
                    why=result.stderr.strip() or "Non-zero exit",
                    action="Check Codex authentication: set OPENAI_API_KEY or run 'codex' interactively",
                )
            if "PREFLIGHT_OK" not in result.stdout:
                raise ConnectivityError(
                    what="Codex not responding correctly",
                    why="Expected PREFLIGHT_OK in output, got something else",
                    action="Verify Codex API access and model availability",
                )
        except FileNotFoundError as e:
            raise ConnectivityError(
                what="Codex CLI not found",
                why="'codex' command not found on PATH",
                action="Install Codex: npm install -g @openai/codex",
            ) from e
        except subprocess.TimeoutExpired as e:
            raise ConnectivityError(
                what="Codex preflight timed out",
                why="Preflight check did not complete within 60 seconds",
                action="Check network connectivity and OpenAI API access",
            ) from e

    def start(
        self,
        story: Path,
        config: Config,
        instructions: Path,
    ) -> subprocess.Popen[str]:
        """Start Codex with the story content as prompt.

        Uses exec subcommand (non-interactive), --full-auto for sandbox,
        and -c developer_instructions for executor instructions.

        Args:
            story: Path to the story markdown file.
            config: Project configuration.
            instructions: Path to executor instructions file.

        Returns:
            Running Codex subprocess.
        """
        worktree = story.parent
        prompt = story.read_text(encoding="utf-8")

        # Copy instructions as AGENTS.md in worktree (Codex auto-discovers this)
        if instructions.exists():
            agents_md = worktree / "AGENTS.md"
            if not agents_md.exists():
                agents_md.write_text(
                    instructions.read_text(encoding="utf-8"), encoding="utf-8"
                )

        cmd = [
            _find_codex(), "exec",
            "--full-auto",
        ]
        if config.reviewer_model:
            cmd.extend(["-m", config.reviewer_model])

        cmd.append(prompt)

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
        """Stream output lines from Codex (FR70).

        Codex writes progress to stderr, final message to stdout.

        Args:
            process: The running Codex subprocess.

        Yields:
            Output lines from stdout.
        """
        if process.stdout is not None:
            for line in process.stdout:
                yield line.rstrip("\n")

    def get_exit_status(
        self, process: subprocess.Popen[str]
    ) -> ExitStatus:
        """Map Codex exit code to ExitStatus (FR71).

        Exit 0 = success, anything else = failure.

        Args:
            process: The completed Codex subprocess.

        Returns:
            ExitStatus based on exit code.
        """
        process.wait()
        if process.returncode == 0:
            return ExitStatus.SUCCESS
        return ExitStatus.FAILURE
