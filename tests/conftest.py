"""Global test fixtures for HPNC.

This module provides shared fixtures used across all test layers.
Fixtures are designed to mirror production layout for realistic testing.

Available fixtures:
    tmp_workspace: Creates a temporary HPNC workspace with config, queue,
        and initialized Git repo. Mirrors production layout.
    mock_executor: Pre-configured mock agent executor returning SUCCESS.
    mock_executor_factory: Factory for creating mock executors with custom config.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

from hpnc.agents.base import ExitStatus
from hpnc.agents.mock import MockAgentExecutor
from hpnc.infra.workspace import Workspace


@pytest.fixture
def tmp_workspace(tmp_path: Path) -> Workspace:
    """Create a temporary HPNC workspace mirroring production layout.

    Creates:
        - _hpnc/config.yaml with project_name: test
        - _hpnc/night-queue.yaml (empty queue)
        - Initialized Git repo with one commit

    Returns:
        Workspace instance rooted at the temporary directory.
    """
    hpnc_dir = tmp_path / "_hpnc"
    hpnc_dir.mkdir()
    (hpnc_dir / "config.yaml").write_text("project_name: test\n")
    (hpnc_dir / "night-queue.yaml").write_text("tasks: []\n")

    subprocess.run(
        ["git", "init"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    (tmp_path / "README.md").write_text("# Test\n")
    subprocess.run(
        ["git", "add", "."],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        check=True,
    )

    return Workspace(root=tmp_path)


@pytest.fixture
def mock_executor() -> MockAgentExecutor:
    """Pre-configured mock agent executor.

    Returns a MockAgentExecutor with default settings:
    ExitStatus.SUCCESS, zero delay, no file changes.
    """
    return MockAgentExecutor(default_status=ExitStatus.SUCCESS, delay=0)


@pytest.fixture
def mock_executor_factory() -> Callable[..., MockAgentExecutor]:
    """Factory fixture for creating mock executors with custom configurations.

    Returns:
        A callable that accepts MockAgentExecutor constructor arguments
        and returns a configured instance.

    Example::

        def test_failure(mock_executor_factory):
            executor = mock_executor_factory(default_status=ExitStatus.FAILURE)
            ...
    """

    def _factory(
        default_status: ExitStatus = ExitStatus.SUCCESS,
        delay: float = 0.0,
        file_changes: list[str] | None = None,
    ) -> MockAgentExecutor:
        return MockAgentExecutor(
            default_status=default_status,
            delay=delay,
            file_changes=file_changes,
        )

    return _factory
