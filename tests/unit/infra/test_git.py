"""Tests for Git subprocess wrapper."""

import subprocess
from pathlib import Path

import pytest

from hpnc.infra.errors import HpncError
from hpnc.infra.git import GitWrapper


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary Git repository with one commit."""
    subprocess.run(
        ["git", "init"], cwd=str(tmp_path),
        capture_output=True, text=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path), capture_output=True, text=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path), capture_output=True, text=True, check=True,
    )
    (tmp_path / "README.md").write_text("# Test\n")
    subprocess.run(
        ["git", "add", "."], cwd=str(tmp_path),
        capture_output=True, text=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"], cwd=str(tmp_path),
        capture_output=True, text=True, check=True,
    )
    return tmp_path


def test_git_create_branch_succeeds(git_repo: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    gw.create_branch("night/test-task")
    result = subprocess.run(
        ["git", "branch", "--list", "night/test-task"],
        cwd=str(git_repo), capture_output=True, text=True,
    )
    assert "night/test-task" in result.stdout


def test_git_checkout_branch_succeeds(git_repo: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    gw.create_branch("feature/test")
    gw.checkout_branch("feature/test")
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=str(git_repo), capture_output=True, text=True,
    )
    assert result.stdout.strip() == "feature/test"


def test_git_create_worktree_succeeds(git_repo: Path, tmp_path: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    gw.create_branch("night/wt-test")
    worktree_path = tmp_path / "worktree"
    gw.create_worktree(worktree_path, "night/wt-test")
    assert worktree_path.exists()
    assert (worktree_path / "README.md").exists()


def test_git_remove_worktree_succeeds(git_repo: Path, tmp_path: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    gw.create_branch("night/remove-test")
    worktree_path = tmp_path / "wt-remove"
    gw.create_worktree(worktree_path, "night/remove-test")
    assert worktree_path.exists()
    gw.remove_worktree(worktree_path)
    assert not worktree_path.exists()


def test_git_list_worktrees_returns_paths(git_repo: Path, tmp_path: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    gw.create_branch("night/list-test")
    worktree_path = tmp_path / "wt-list"
    gw.create_worktree(worktree_path, "night/list-test")
    worktrees = gw.list_worktrees()
    assert len(worktrees) >= 2  # main repo + new worktree
    paths_str = [str(p) for p in worktrees]
    assert any("wt-list" in p for p in paths_str)


def test_git_invalid_command_raises(git_repo: Path) -> None:
    gw = GitWrapper(repo_root=git_repo)
    with pytest.raises(HpncError):
        gw.checkout_branch("nonexistent-branch-xyz")
