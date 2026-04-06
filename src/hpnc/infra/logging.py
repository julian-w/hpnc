"""Logging setup — stdlib logging with Rich terminal handler (FR76, FR77).

Configurable verbosity (minimal/normal/verbose) and agent output capture
modes (full/truncated/none). Timestamps included at all levels (NFR5).
"""

from __future__ import annotations

import logging
from enum import Enum
from pathlib import Path

from rich.logging import RichHandler

__all__ = ["AgentOutputMode", "setup_logging"]

_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

VERBOSITY_MAP: dict[str, int] = {
    "minimal": logging.WARNING,
    "normal": logging.INFO,
    "verbose": logging.DEBUG,
}
"""Maps verbosity config strings to logging levels."""


class AgentOutputMode(Enum):
    """Agent output capture mode (FR77)."""

    FULL = "full"
    TRUNCATED = "truncated"
    NONE = "none"


# Module-level config for downstream access
_agent_output_mode: AgentOutputMode = AgentOutputMode.FULL


def get_agent_output_mode() -> AgentOutputMode:
    """Get the current agent output capture mode.

    Returns:
        The configured AgentOutputMode.
    """
    return _agent_output_mode


def setup_logging(
    verbosity: str = "normal",
    log_file: Path | None = None,
    agent_output: str = "full",
) -> logging.Logger:
    """Configure logging for an HPNC run.

    Sets up a Rich terminal handler and optionally a file handler.
    Timestamps are included at all verbosity levels (NFR5).

    Args:
        verbosity: Log verbosity — "minimal", "normal", or "verbose".
        log_file: Optional path to a log file for persistent logging.
        agent_output: Agent output capture mode — "full", "truncated", or "none".

    Returns:
        The configured root logger for the hpnc namespace.
    """
    global _agent_output_mode  # noqa: PLW0603
    _agent_output_mode = AgentOutputMode(agent_output)

    level = VERBOSITY_MAP.get(verbosity, logging.INFO)

    hpnc_logger = logging.getLogger("hpnc")
    hpnc_logger.setLevel(level)
    hpnc_logger.handlers.clear()

    # Terminal handler — Rich for colored output
    rich_handler = RichHandler(
        level=level,
        show_time=True,
        show_path=False,
        markup=True,
    )
    hpnc_logger.addHandler(rich_handler)

    # File handler — plain text with timestamps
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            str(log_file), encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter(_LOG_FORMAT, datefmt=_LOG_DATE_FORMAT)
        )
        hpnc_logger.addHandler(file_handler)

    return hpnc_logger
