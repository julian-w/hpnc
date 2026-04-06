"""FileEventListener — writes task status updates to run.yaml (Phase 1).

Stub implementation. Full implementation in Story 2.3.
"""

from __future__ import annotations

from pathlib import Path

from hpnc.core.state_machine import TaskState
from hpnc.events.base import RunResult

__all__ = ["FileEventListener"]


class FileEventListener:
    """Writes task lifecycle events to run.yaml in the run directory.

    Args:
        run_dir: Directory where run.yaml will be written.
    """

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir

    def on_status_change(
        self, task: str, old: TaskState, new: TaskState
    ) -> None:
        """Called when a task transitions between states.

        Args:
            task: The task identifier.
            old: The previous state.
            new: The new state.
        """
        raise NotImplementedError("Implemented in Story 2.3")

    def on_progress(
        self, task: str, phase: str, detail: str
    ) -> None:
        """Called to report progress within a phase.

        Args:
            task: The task identifier.
            phase: The current phase name.
            detail: Progress detail message.
        """
        raise NotImplementedError("Implemented in Story 2.3")

    def on_complete(self, task: str, result: RunResult) -> None:
        """Called when a task reaches a terminal state.

        Args:
            task: The task identifier.
            result: The final run result.
        """
        raise NotImplementedError("Implemented in Story 2.3")
