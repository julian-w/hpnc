"""Tests for agent routing."""

import pytest

from hpnc.agents.base import AgentExecutor
from hpnc.agents.claude_code import ClaudeCodeExecutor
from hpnc.agents.codex import CodexExecutor
from hpnc.agents.mock import MockAgentExecutor
from hpnc.agents.routing import get_executor
from hpnc.infra.errors import ConfigError


def test_get_executor_opus_returns_claude_code() -> None:
    executor = get_executor("opus")
    assert isinstance(executor, ClaudeCodeExecutor)


def test_get_executor_claude_returns_claude_code() -> None:
    executor = get_executor("claude")
    assert isinstance(executor, ClaudeCodeExecutor)


def test_get_executor_codex_returns_codex() -> None:
    executor = get_executor("codex")
    assert isinstance(executor, CodexExecutor)


def test_get_executor_mock_returns_mock() -> None:
    executor = get_executor("mock")
    assert isinstance(executor, MockAgentExecutor)


def test_get_executor_case_insensitive() -> None:
    assert isinstance(get_executor("OPUS"), ClaudeCodeExecutor)
    assert isinstance(get_executor("Codex"), CodexExecutor)


def test_get_executor_unknown_raises() -> None:
    with pytest.raises(ConfigError, match="Unknown agent"):
        get_executor("gpt-5")


def test_claude_code_executor_satisfies_protocol() -> None:
    assert isinstance(ClaudeCodeExecutor(), AgentExecutor)


def test_codex_executor_satisfies_protocol() -> None:
    assert isinstance(CodexExecutor(), AgentExecutor)
