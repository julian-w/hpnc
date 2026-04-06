"""TaskEventListener Protocol — interface for task status updates.

Phase 1: FileEventListener writes to run.yaml.
Future: AsyncEventListener, WebSocketEventListener.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from hpnc.core.state_machine import TaskState

__all__ = ["RunResult", "TaskEventListener"]


@dataclass
class RunResult:
    """Result of a completed task run, mirroring run.yaml fields."""

    status: TaskState
    executor: str
    reviewer: str
    branch: str
    started: str
    finished: str
    files_changed: list[str] = field(default_factory=list)
    story_source: str = ""


@runtime_checkable
class TaskEventListener(Protocol):
    """Interface for receiving task lifecycle events.

    Implementations are injected into Task-Runner via constructor.
    """

    def on_status_change(
        self, task: str, old: TaskState, new: TaskState
    ) -> None:
        """Called when a task transitions between states.

        Args:
            task: The task identifier.
            old: The previous state.
            new: The new state.
        """
        ...

    def on_progress(
        self, task: str, phase: str, detail: str
    ) -> None:
        """Called to report progress within a phase.

        Args:
            task: The task identifier.
            phase: The current phase name.
            detail: Progress detail message.
        """
        ...

    def on_complete(self, task: str, result: RunResult) -> None:
        """Called when a task reaches a terminal state.

        Args:
            task: The task identifier.
            result: The final run result.
        """
        ...
