"""HPNC error hierarchy with structured error messages (NFR24).

Every error carries three fields: what happened, why, and what to do.
CLI layer catches HpncError and formats output with Rich.
"""

from __future__ import annotations

__all__ = [
    "HpncError",
    "ConfigError",
    "ConnectivityError",
    "ValidationError",
    "TaskBlockedError",
    "TaskInterruptedError",
    "InvalidTransitionError",
]


class HpncError(Exception):
    """Base error with what/why/action fields (NFR24).

    Args:
        what: What happened — a concise description of the error.
        why: Why it happened — the root cause or context.
        action: What to do — actionable guidance to resolve the issue.
    """

    exit_code: int = 1

    def __init__(self, what: str, why: str, action: str) -> None:
        self.what = what
        self.why = why
        self.action = action
        super().__init__(f"{what}: {why}")

    def __str__(self) -> str:
        return f"{self.what}: {self.why}\n  Action: {self.action}"


class ValidationError(HpncError):
    """Frontmatter or pre-flight validation failure."""

    exit_code: int = 1


class TaskBlockedError(HpncError):
    """Agent cannot proceed without human input."""

    exit_code: int = 2


class TaskInterruptedError(HpncError):
    """Process terminated unexpectedly."""

    exit_code: int = 3


class ConfigError(HpncError):
    """Config file missing, invalid, or unreadable."""

    exit_code: int = 4


class ConnectivityError(HpncError):
    """Agent CLI not reachable."""

    exit_code: int = 5


class InvalidTransitionError(HpncError):
    """Invalid state machine transition attempted."""

    exit_code: int = 1
