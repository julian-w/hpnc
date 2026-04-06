"""Git subprocess wrapper — thin abstraction for all Git operations.

Uses subprocess.run() with capture_output=True, never shell=True.
All paths use pathlib.Path and are converted to str for subprocess calls.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from hpnc.infra.errors import HpncError

__all__ = ["GitWrapper"]


class GitWrapper:
    """Subprocess-based Git operations for a repository.

    Enables Windows long-path support (core.longpaths) automatically (NFR30).

    Args:
        repo_root: Path to the Git repository root.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        if sys.platform == "win32":
            self._enable_longpaths()

    def _enable_longpaths(self) -> None:
        """Enable Git long-path support on Windows (NFR30).

        Sets core.longpaths=true for the repository to handle paths
        exceeding the default 260-character Windows limit.
        """
        subprocess.run(
            ["git", "config", "core.longpaths", "true"],
            capture_output=True,
            text=True,
            cwd=str(self.repo_root),
        )

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        """Execute a git command and return the result.

        Args:
            args: Git subcommand and arguments (without 'git' prefix).

        Returns:
            The completed process result.

        Raises:
            HpncError: If the git command exits with non-zero status.
        """
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            cwd=str(self.repo_root),
        )
        if result.returncode != 0:
            cmd_str = f"git {' '.join(args)}"
            raise HpncError(
                what=f"Git command failed: {cmd_str}",
                why=result.stderr.strip() or f"Exit code {result.returncode}",
                action="Check git status and repository state",
            )
        return result

    def create_branch(self, name: str) -> None:
        """Create a new branch.

        Args:
            name: Branch name (e.g., 'night/login-validation').
        """
        self._run(["branch", "--", name])

    def checkout_branch(self, name: str) -> None:
        """Switch to an existing branch.

        Args:
            name: Branch name to check out.
        """
        self._run(["checkout", name])

    def create_worktree(self, path: Path, branch: str) -> None:
        """Create a Git worktree at the given path for the given branch.

        Args:
            path: Directory where the worktree will be created.
            branch: Branch name to check out in the worktree.
        """
        self._run(["worktree", "add", str(path), branch])

    def remove_worktree(self, path: Path) -> None:
        """Remove a Git worktree.

        Args:
            path: Path to the worktree to remove.
        """
        self._run(["worktree", "remove", str(path), "--force"])

    def list_worktrees(self) -> list[Path]:
        """List all worktrees for the repository.

        Returns:
            List of worktree directory paths.
        """
        result = self._run(["worktree", "list", "--porcelain"])
        worktrees: list[Path] = []
        for line in result.stdout.splitlines():
            if line.startswith("worktree "):
                worktrees.append(Path(line.removeprefix("worktree ").strip()))
        return worktrees
