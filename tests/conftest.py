"""Global test fixtures for HPNC.

This module provides shared fixtures used across all test layers.
Fixtures are designed to mirror production layout for realistic testing.

Available fixtures:
    mock_executor: Pre-configured mock agent executor returning SUCCESS.
    mock_executor_factory: Factory for creating mock executors with custom config.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from hpnc.agents.base import ExitStatus
from hpnc.agents.mock import MockAgentExecutor


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
