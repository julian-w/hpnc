"""FileEventListener — writes task status updates to run.yaml (Phase 1).

Persists every state transition immediately via Workspace.write_yaml_atomic().
No batching, no buffering — crash safety is the priority (NFR2).
"""

from __future__ import annotations

import logging
from pathlib import Path

from hpnc.core.state_machine import TaskState
from hpnc.events.base import RunResult
from hpnc.infra.workspace import Workspace

__all__ = ["FileEventListener"]

logger = logging.getLogger(__name__)


class FileEventListener:
    """Writes task lifecycle events to run.yaml in the run directory.

    Uses Workspace.write_yaml_atomic() for all writes to ensure
    atomic persistence of every state transition (NFR2, NFR11).

    Args:
        run_dir: Directory where run.yaml will be written.
        workspace: Workspace instance for atomic file operations.
    """

    def __init__(self, run_dir: Path, workspace: Workspace) -> None:
        self.run_dir = run_dir
        self.workspace = workspace
        self._run_yaml = run_dir / "run.yaml"

    def on_status_change(
        self, task: str, old: TaskState, new: TaskState
    ) -> None:
        """Persist a state transition to run.yaml immediately.

        Args:
            task: The task identifier.
            old: The previous state.
            new: The new state.
        """
        logger.info("Task %s: %s -> %s", task, old.value, new.value)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.workspace.write_yaml_atomic(
            self._run_yaml,
            {
                "task": task,
                "status": new.value,
                "previous_status": old.value,
            },
        )

    def on_progress(
        self, task: str, phase: str, detail: str
    ) -> None:
        """Log progress within a phase.

        Args:
            task: The task identifier.
            phase: The current phase name.
            detail: Progress detail message.
        """
        logger.info("Task %s [%s]: %s", task, phase, detail)

    def on_complete(self, task: str, result: RunResult) -> None:
        """Write final RunResult to run.yaml with all mandatory fields (FR50).

        Args:
            task: The task identifier.
            result: The final run result.
        """
        logger.info("Task %s completed: %s", task, result.status.value)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.workspace.write_yaml_atomic(
            self._run_yaml,
            {
                "status": result.status.value,
                "executor": result.executor,
                "reviewer": result.reviewer,
                "branch": result.branch,
                "started": result.started,
                "finished": result.finished,
                "files_changed": result.files_changed,
                "story_source": result.story_source,
            },
        )
