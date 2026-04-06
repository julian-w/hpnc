"""Integration tests for Dispatcher sequential task processing."""

from pathlib import Path

import yaml

from hpnc.agents.base import ExitStatus
from hpnc.agents.mock import MockAgentExecutor
from hpnc.core.dispatcher import Dispatcher
from hpnc.core.queue_manager import QueueManager
from hpnc.core.state_machine import TaskState
from hpnc.gates.runner import GateResult, GateRunner
from hpnc.infra.config import Config
from hpnc.infra.git import GitWrapper
from hpnc.infra.process_lock import ProcessLock
from hpnc.infra.workspace import Workspace


class _PassGate:
    @property
    def name(self) -> str:
        return "mock-pass"

    def run(self, worktree: Path) -> GateResult:
        return GateResult(name=self.name, passed=True, exit_code=0)


def _setup_dispatcher(
    tmp_workspace: Workspace,
    stories: int = 2,
    executor_status: ExitStatus = ExitStatus.SUCCESS,
) -> tuple[Dispatcher, Path, Path]:
    """Create Dispatcher with mock tasks in queue."""
    root = tmp_workspace.root
    config = Config(project_name="test", project_root=root)
    git = GitWrapper(repo_root=root)

    # Create queue with stories
    queue_path = root / "_hpnc" / "night-queue.yaml"
    tasks = []
    for i in range(stories):
        story = root / f"story-{i}.md"
        story.write_text(f"---\nnight_ready: true\n---\n\n# Story {i}\n")
        tasks.append({"story": str(story)})
    tmp_workspace.write_yaml_atomic(queue_path, {"tasks": tasks})

    # Create instructions file
    instructions = root / "_hpnc" / "executor-instructions.md"
    instructions.write_text("# Instructions\n")

    queue_manager = QueueManager(workspace=tmp_workspace, queue_path=queue_path)
    lock = ProcessLock(lock_path=root / "_hpnc" / ".dispatcher.lock")

    executor = MockAgentExecutor(default_status=executor_status)
    reviewer = MockAgentExecutor(default_status=ExitStatus.SUCCESS)
    gates = GateRunner(gates=[_PassGate()])  # type: ignore[list-item]

    dispatcher = Dispatcher(
        executor=executor,
        reviewer=reviewer,
        gates=gates,
        workspace=tmp_workspace,
        config=config,
        git=git,
        queue_manager=queue_manager,
        lock=lock,
    )

    worktree_base = root / "worktrees"
    run_dir_base = root / "_hpnc" / "runs" / "test"

    return dispatcher, worktree_base, run_dir_base


def test_dispatcher_processes_multiple_tasks(tmp_workspace: Workspace) -> None:
    dispatcher, wt_base, run_base = _setup_dispatcher(tmp_workspace, stories=3)
    results = dispatcher.run(wt_base, run_base)
    assert len(results) == 3
    assert all(r.status == TaskState.DONE for r in results)


def test_dispatcher_persists_state_after_each_task(tmp_workspace: Workspace) -> None:
    dispatcher, wt_base, run_base = _setup_dispatcher(tmp_workspace, stories=2)
    dispatcher.run(wt_base, run_base)

    state_path = tmp_workspace.root / "_hpnc" / "dispatcher-state.yaml"
    assert state_path.exists()
    state = yaml.safe_load(state_path.read_text())
    assert state["status"] == "completed"
    assert state["completed"] == 2


def test_dispatcher_lock_prevents_double_start(tmp_workspace: Workspace) -> None:
    root = tmp_workspace.root
    lock = ProcessLock(lock_path=root / "_hpnc" / ".dispatcher.lock")

    # Acquire lock externally
    lock.acquire()
    try:
        dispatcher, wt_base, run_base = _setup_dispatcher(tmp_workspace, stories=1)
        # This should fail because lock is held
        import pytest

        from hpnc.infra.errors import HpncError
        with pytest.raises(HpncError):
            dispatcher.run(wt_base, run_base)
    finally:
        lock.release()


def test_dispatcher_handles_blocked_tasks(tmp_workspace: Workspace) -> None:
    dispatcher, wt_base, run_base = _setup_dispatcher(
        tmp_workspace, stories=2, executor_status=ExitStatus.FAILURE
    )
    results = dispatcher.run(wt_base, run_base)
    assert len(results) == 2
    assert all(r.status == TaskState.BLOCKED for r in results)
