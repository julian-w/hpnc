"""Edge case tests for Dispatcher."""

from pathlib import Path

import yaml

from hpnc.agents.mock import MockAgentExecutor
from hpnc.core.dispatcher import Dispatcher
from hpnc.core.queue_manager import QueueManager
from hpnc.gates.runner import GateResult, GateRunner
from hpnc.infra.config import Config
from hpnc.infra.git import GitWrapper
from hpnc.infra.process_lock import ProcessLock
from hpnc.infra.workspace import Workspace


class _PassGate:
    @property
    def name(self) -> str:
        return "pass"

    def run(self, worktree: Path) -> GateResult:
        return GateResult(name=self.name, passed=True, exit_code=0)


def _setup(
    tmp_workspace: Workspace,
    stories: int = 1,
) -> tuple[Dispatcher, Path, Path]:
    root = tmp_workspace.root
    config = Config(project_name="test", project_root=root)
    git = GitWrapper(repo_root=root)
    queue_path = root / "_hpnc" / "night-queue.yaml"

    tasks = []
    for i in range(stories):
        story = root / f"story-{i}.md"
        story.write_text(f"---\nnight_ready: true\n---\n\n# Story {i}\n")
        tasks.append({"story": str(story)})
    tmp_workspace.write_yaml_atomic(queue_path, {"tasks": tasks})

    (root / "_hpnc" / "executor-instructions.md").write_text("# Instructions\n")

    qm = QueueManager(workspace=tmp_workspace, queue_path=queue_path)
    lock = ProcessLock(lock_path=root / "_hpnc" / ".dispatcher.lock")

    dispatcher = Dispatcher(
        executor=MockAgentExecutor(),
        reviewer=MockAgentExecutor(),
        gates=GateRunner(gates=[_PassGate()]),  # type: ignore[list-item]
        workspace=tmp_workspace,
        config=config,
        git=git,
        queue_manager=qm,
        lock=lock,
    )

    return dispatcher, root / "worktrees", root / "_hpnc" / "runs" / "test"


def test_dispatcher_empty_queue_returns_empty(tmp_workspace: Workspace) -> None:
    root = tmp_workspace.root
    config = Config(project_name="test", project_root=root)
    git = GitWrapper(repo_root=root)
    queue_path = root / "_hpnc" / "night-queue.yaml"
    tmp_workspace.write_yaml_atomic(queue_path, {"tasks": []})

    qm = QueueManager(workspace=tmp_workspace, queue_path=queue_path)
    lock = ProcessLock(lock_path=root / "_hpnc" / ".dispatcher.lock")

    dispatcher = Dispatcher(
        executor=MockAgentExecutor(),
        reviewer=MockAgentExecutor(),
        gates=GateRunner(gates=[]),
        workspace=tmp_workspace,
        config=config,
        git=git,
        queue_manager=qm,
        lock=lock,
    )

    results = dispatcher.run(root / "wt", root / "_hpnc" / "runs" / "test")
    assert results == []


def test_dispatcher_state_shows_completed_count(tmp_workspace: Workspace) -> None:
    dispatcher, wt, run_base = _setup(tmp_workspace, stories=3)
    dispatcher.run(wt, run_base)

    state_path = tmp_workspace.root / "_hpnc" / "dispatcher-state.yaml"
    state = yaml.safe_load(state_path.read_text())
    assert state["completed"] == 3
    assert state["status"] == "completed"


def test_dispatcher_queue_emptied_after_run(tmp_workspace: Workspace) -> None:
    dispatcher, wt, run_base = _setup(tmp_workspace, stories=2)
    dispatcher.run(wt, run_base)

    queue_path = tmp_workspace.root / "_hpnc" / "night-queue.yaml"
    queue = yaml.safe_load(queue_path.read_text())
    assert queue["tasks"] == []
