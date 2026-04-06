"""Dispatcher — sequential task processing with state persistence (FR32-FR34).

Acquires ProcessLock, processes tasks from queue via TaskRunner,
persists state after each task, cleans up completed tasks.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from hpnc.agents.base import AgentExecutor
from hpnc.core.queue_manager import QueueManager
from hpnc.core.task_runner import TaskRunner
from hpnc.events.base import RunResult
from hpnc.events.file_listener import FileEventListener
from hpnc.gates.runner import GateRunner
from hpnc.infra.config import Config
from hpnc.infra.git import GitWrapper
from hpnc.infra.process_lock import ProcessLock
from hpnc.infra.workspace import Workspace

__all__ = ["Dispatcher", "DispatcherState"]

logger = logging.getLogger(__name__)


class DispatcherState:
    """Persists dispatcher progress to disk after each task.

    Args:
        workspace: Workspace for atomic file operations.
        state_path: Path to dispatcher-state.yaml.
    """

    def __init__(self, workspace: Workspace, state_path: Path) -> None:
        self.workspace = workspace
        self.state_path = state_path

    def save(self, data: dict[str, Any]) -> None:
        """Persist current state atomically.

        Args:
            data: State dict to write.
        """
        self.workspace.write_yaml_atomic(self.state_path, data)

    def load(self) -> dict[str, Any]:
        """Load persisted state, or empty dict if none exists.

        Returns:
            Saved state dict.
        """
        try:
            return self.workspace.read_yaml(self.state_path)
        except Exception:
            return {}

    def clear(self) -> None:
        """Remove the state file after successful completion."""
        try:
            self.state_path.unlink()
        except OSError:
            pass


class Dispatcher:
    """Orchestrates sequential task processing for a night run.

    Args:
        executor: AgentExecutor for implementation.
        reviewer: AgentExecutor for review.
        gates: GateRunner for quality gates.
        workspace: Workspace for file operations.
        config: Project configuration.
        git: GitWrapper for branch/worktree operations.
        queue_manager: QueueManager for reading/writing the queue.
        lock: ProcessLock for exclusivity.
    """

    def __init__(
        self,
        executor: AgentExecutor,
        reviewer: AgentExecutor,
        gates: GateRunner,
        workspace: Workspace,
        config: Config,
        git: GitWrapper,
        queue_manager: QueueManager,
        lock: ProcessLock,
    ) -> None:
        self.executor = executor
        self.reviewer = reviewer
        self.gates = gates
        self.workspace = workspace
        self.config = config
        self.git = git
        self.queue_manager = queue_manager
        self.lock = lock

    def run(self, worktree_base: Path, run_dir_base: Path) -> list[RunResult]:
        """Process all queued tasks sequentially.

        Acquires the ProcessLock, iterates through queued tasks,
        runs each through TaskRunner, persists state after each completion,
        and cleans up completed tasks from the queue.

        Args:
            worktree_base: Base directory for creating worktrees.
            run_dir_base: Base directory for run artifacts.

        Returns:
            List of RunResults for all processed tasks.
        """
        results: list[RunResult] = []
        state_path = self.config.project_root / "_hpnc" / "dispatcher-state.yaml"
        state = DispatcherState(workspace=self.workspace, state_path=state_path)

        with self.lock:
            started = datetime.now(tz=UTC).isoformat()
            tasks = self.queue_manager.list_tasks()
            logger.info("Dispatcher started: %d task(s) in queue", len(tasks))

            state.save({
                "status": "running",
                "started": started,
                "total_tasks": len(tasks),
                "completed": 0,
            })

            for i, task in enumerate(tasks):
                story_path = Path(task.get("story", ""))
                task_name = story_path.stem
                run_dir = run_dir_base / task_name

                logger.info("Processing task %d/%d: %s", i + 1, len(tasks), task_name)

                listener = FileEventListener(
                    run_dir=run_dir, workspace=self.workspace
                )
                instructions = self.config.project_root / "_hpnc" / "executor-instructions.md"

                runner = TaskRunner(
                    executor=self.executor,
                    reviewer=self.reviewer,
                    gates=self.gates,
                    listener=listener,
                    workspace=self.workspace,
                    config=self.config,
                    git=self.git,
                    executor_name=self.config.executor,
                    reviewer_name=self.config.reviewer,
                )

                worktree_base.mkdir(parents=True, exist_ok=True)
                result = runner.run(
                    task_name=task_name,
                    story=story_path,
                    instructions=instructions,
                    worktree_base=worktree_base,
                )
                results.append(result)

                # Persist state after each task (NFR2, FR33)
                state.save({
                    "status": "running",
                    "started": started,
                    "total_tasks": len(tasks),
                    "completed": i + 1,
                    "last_task": task_name,
                    "last_status": result.status.value,
                })

                logger.info(
                    "Task %s completed: %s", task_name, result.status.value
                )

            # Clean up completed tasks from queue (FR34)
            # All processed tasks are removed — they have terminal status in run artifacts
            self.workspace.write_yaml_atomic(
                self.queue_manager.queue_path, {"tasks": []}
            )

            state.save({
                "status": "completed",
                "started": started,
                "finished": datetime.now(tz=UTC).isoformat(),
                "total_tasks": len(tasks),
                "completed": len(tasks),
                "results": [
                    {"task": Path(t.get("story", "")).stem, "status": r.status.value}
                    for t, r in zip(tasks, results, strict=True)
                ],
            })

            logger.info("Dispatcher completed: %d task(s) processed", len(results))

        return results
