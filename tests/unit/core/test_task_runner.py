"""Unit tests for TaskRunner error handling and edge cases."""

from pathlib import Path
from unittest.mock import MagicMock

from hpnc.agents.base import ExitStatus
from hpnc.agents.mock import MockAgentExecutor
from hpnc.core.state_machine import TaskState
from hpnc.core.task_runner import TaskRunner
from hpnc.events.file_listener import FileEventListener
from hpnc.gates.runner import GateResult, GateRunner
from hpnc.infra.config import Config
from hpnc.infra.errors import HpncError
from hpnc.infra.git import GitWrapper
from hpnc.infra.workspace import Workspace


class _FailGate:
    @property
    def name(self) -> str:
        return "fail"

    def run(self, worktree: Path) -> GateResult:
        return GateResult(name="fail", passed=False, exit_code=1, stderr="failed")


def _make_runner(
    tmp_workspace: Workspace,
    executor_status: ExitStatus = ExitStatus.SUCCESS,
    gates_pass: bool = True,
) -> tuple[TaskRunner, Path, Path, Path]:
    root = tmp_workspace.root
    git = GitWrapper(repo_root=root)
    run_dir = root / "_hpnc" / "runs" / "test"
    listener = FileEventListener(run_dir=run_dir, workspace=tmp_workspace)
    config = Config(project_name="test", project_root=root)

    gate_list: list[object] = []
    if not gates_pass:
        gate_list = [_FailGate()]
    gates = GateRunner(gates=gate_list)  # type: ignore[arg-type]

    runner = TaskRunner(
        executor=MockAgentExecutor(default_status=executor_status),
        reviewer=MockAgentExecutor(),
        gates=gates,
        listener=listener,
        workspace=tmp_workspace,
        config=config,
        git=git,
    )

    story = root / "story.md"
    story.write_text("# Test\n")
    instructions = root / "instructions.md"
    instructions.write_text("# Instr\n")
    wt_base = root / "worktrees"
    wt_base.mkdir()

    return runner, story, instructions, wt_base


def test_task_runner_returns_done_on_success(tmp_workspace: Workspace) -> None:
    runner, story, instr, wt = _make_runner(tmp_workspace)
    result = runner.run("ok-task", story, instr, wt)
    assert result.status == TaskState.DONE


def test_task_runner_returns_blocked_on_executor_failure(tmp_workspace: Workspace) -> None:
    runner, story, instr, wt = _make_runner(
        tmp_workspace, executor_status=ExitStatus.FAILURE
    )
    result = runner.run("block-task", story, instr, wt)
    assert result.status == TaskState.BLOCKED


def test_task_runner_returns_failed_on_gate_failure(tmp_workspace: Workspace) -> None:
    runner, story, instr, wt = _make_runner(tmp_workspace, gates_pass=False)
    result = runner.run("fail-task", story, instr, wt)
    assert result.status == TaskState.FAILED


def test_task_runner_cleans_worktree_on_success(tmp_workspace: Workspace) -> None:
    runner, story, instr, wt = _make_runner(tmp_workspace)
    runner.run("clean-task", story, instr, wt)
    assert not (wt / "clean-task").exists()


def test_task_runner_cleans_worktree_on_failure(tmp_workspace: Workspace) -> None:
    runner, story, instr, wt = _make_runner(tmp_workspace, gates_pass=False)
    runner.run("fail-clean", story, instr, wt)
    assert not (wt / "fail-clean").exists()


def test_task_runner_fires_listener_on_every_transition(tmp_workspace: Workspace) -> None:
    root = tmp_workspace.root
    listener = MagicMock()
    config = Config(project_name="test", project_root=root)
    git = GitWrapper(repo_root=root)

    runner = TaskRunner(
        executor=MockAgentExecutor(),
        reviewer=MockAgentExecutor(),
        gates=GateRunner(gates=[]),
        listener=listener,
        workspace=tmp_workspace,
        config=config,
        git=git,
    )

    story = root / "story.md"
    story.write_text("# Test\n")
    instr = root / "instr.md"
    instr.write_text("# I\n")
    wt = root / "wt"
    wt.mkdir()

    runner.run("listen-task", story, instr, wt)

    # Should have multiple on_status_change calls
    assert listener.on_status_change.call_count >= 4  # QUEUED->SETUP->IMPL->REVIEW->GATES->DONE
    assert listener.on_complete.call_count == 1


def test_task_runner_result_has_executor_reviewer_names(tmp_workspace: Workspace) -> None:
    root = tmp_workspace.root
    git = GitWrapper(repo_root=root)
    run_dir = root / "_hpnc" / "runs" / "test"
    listener = FileEventListener(run_dir=run_dir, workspace=tmp_workspace)
    config = Config(project_name="test", project_root=root)

    runner = TaskRunner(
        executor=MockAgentExecutor(),
        reviewer=MockAgentExecutor(),
        gates=GateRunner(gates=[]),
        listener=listener,
        workspace=tmp_workspace,
        config=config,
        git=git,
        executor_name="opus",
        reviewer_name="codex",
    )

    story = root / "story.md"
    story.write_text("# Test\n")
    instr = root / "instr.md"
    instr.write_text("# I\n")
    wt = root / "wt"
    wt.mkdir()

    result = runner.run("name-task", story, instr, wt)
    assert result.executor == "opus"
    assert result.reviewer == "codex"


def test_task_runner_handles_git_error_gracefully(tmp_workspace: Workspace) -> None:
    """If git operations fail, task should still return a result."""
    root = tmp_workspace.root
    listener = MagicMock()
    config = Config(project_name="test", project_root=root)

    # Create a GitWrapper that will fail on create_branch
    git = MagicMock()
    git.create_branch.side_effect = HpncError(
        what="branch exists", why="already exists", action="delete first"
    )

    runner = TaskRunner(
        executor=MockAgentExecutor(),
        reviewer=MockAgentExecutor(),
        gates=GateRunner(gates=[]),
        listener=listener,
        workspace=tmp_workspace,
        config=config,
        git=git,
    )

    story = root / "story.md"
    story.write_text("# Test\n")
    instr = root / "instr.md"
    instr.write_text("# I\n")
    wt = root / "wt"
    wt.mkdir()

    result = runner.run("git-fail", story, instr, wt)
    assert result.status == TaskState.FAILED
