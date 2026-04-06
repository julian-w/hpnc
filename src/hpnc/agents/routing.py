"""Agent routing — selects executor/reviewer based on story frontmatter (FR72-FR73).

Maps agent identifiers from frontmatter to concrete AgentExecutor implementations.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from hpnc.agents.base import AgentExecutor
from hpnc.agents.claude_code import ClaudeCodeExecutor
from hpnc.agents.codex import CodexExecutor
from hpnc.agents.mock import MockAgentExecutor
from hpnc.infra.errors import ConfigError

__all__ = ["get_executor"]

_REGISTRY: dict[str, Callable[[], Any]] = {
    "opus": ClaudeCodeExecutor,
    "claude": ClaudeCodeExecutor,
    "codex": CodexExecutor,
    "mock": MockAgentExecutor,
}


def get_executor(name: str) -> AgentExecutor:
    """Get an AgentExecutor instance by name.

    Args:
        name: Agent identifier from frontmatter (e.g., "opus", "codex", "mock").

    Returns:
        Configured AgentExecutor instance.

    Raises:
        ConfigError: If the agent name is not recognized.
    """
    if not name or not isinstance(name, str):
        raise ConfigError(
            what="No agent specified",
            why="executor/reviewer field is empty or missing in config",
            action=f"Set executor/reviewer to one of: {', '.join(sorted(_REGISTRY.keys()))}",
        )
    factory = _REGISTRY.get(name.lower())
    if factory is None:
        raise ConfigError(
            what=f"Unknown agent: {name}",
            why=f"Supported agents: {', '.join(sorted(_REGISTRY.keys()))}",
            action=f"Use one of: {', '.join(sorted(_REGISTRY.keys()))}",
        )
    result: AgentExecutor = factory()
    return result
