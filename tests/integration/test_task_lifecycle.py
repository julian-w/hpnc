"""Integration tests for TaskRunner complete lifecycle."""

from pathlib import Path

import yaml

from hpnc.agents.base import ExitStatus
from hpnc.agents.mock import MockAgentExecutor
from hpnc.core.state_machine import TaskState
from hpnc.core.task_runner import TaskRunner
from hpnc.events.file_listener import FileEventListener
from hpnc.gates.runner import GateResult, GateRunner
from hpnc.infra.config import Config
from hpnc.infra.git import GitWrapper
from hpnc.infra.workspace import Workspace


class _AlwaysPassGate:
    """Mock gate that always passes."""

    @property
    def name(self) -> str:
        return "mock-pass"

    def run(self, worktree: Path) -> GateResult:
        return GateResult(name=self.name, passed=True, exit_code=0)


class _AlwaysFailGate:
    """Mock gate that always fails."""

    @property
    def name(self) -> str:
        return "mock-fail"

    def run(self, worktree: Path) -> GateResult:
        return GateResult(
            name=self.name, passed=False, exit_code=1, stderr="gate failed"
        )


def _setup_runner(
    tmp_workspace: Workspace,
    executor_status: ExitStatus = ExitStatus.SUCCESS,
    reviewer_status: ExitStatus = ExitStatus.SUCCESS,
    gates_pass: bool = True,
) -> tuple[TaskRunner, Path, Path, Path]:
    """Create a configured TaskRunner with the given mock behaviors.

    Returns:
        Tuple of (runner, story_path, instructions_path, worktree_base).
    """
    root = tmp_workspace.root
    git = GitWrapper(repo_root=root)
    run_dir = root / "_hpnc" / "runs" / "test"
    listener = FileEventListener(run_dir=run_dir, workspace=tmp_workspace)
    config = Config(project_name="test", project_root=root)

    executor = MockAgentExecutor(default_status=executor_status)
    reviewer = MockAgentExecutor(default_status=reviewer_status)

    gate_list = [_AlwaysPassGate()] if gates_pass else [_AlwaysFailGate()]
    gates = GateRunner(gates=gate_list)  # type: ignore[list-item]

    runner = TaskRunner(
        executor=executor,
        reviewer=reviewer,
        gates=gates,
        listener=listener,
        workspace=tmp_workspace,
        config=config,
        git=git,
    )

    story = root / "story.md"
    story.write_text("# Test Story\n")
    instructions = root / "instructions.md"
    instructions.write_text("# Instructions\n")
    worktree_base = root / "worktrees"
    worktree_base.mkdir()

    return runner, story, instructions, worktree_base


def test_task_lifecycle_queued_to_done(tmp_workspace: Workspace) -> None:
    runner, story, instructions, wt_base = _setup_runner(tmp_workspace)
    result = runner.run("test-task", story, instructions, wt_base)
    assert result.status == TaskState.DONE


def test_task_lifecycle_queued_to_failed(tmp_workspace: Workspace) -> None:
    runner, story, instructions, wt_base = _setup_runner(
        tmp_workspace, gates_pass=False
    )
    result = runner.run("fail-task", story, instructions, wt_base)
    assert result.status == TaskState.FAILED


def test_task_lifecycle_queued_to_blocked(tmp_workspace: Workspace) -> None:
    runner, story, instructions, wt_base = _setup_runner(
        tmp_workspace, executor_status=ExitStatus.FAILURE
    )
    result = runner.run("block-task", story, instructions, wt_base)
    assert result.status == TaskState.BLOCKED


def test_task_lifecycle_worktree_cleaned_up_on_done(
    tmp_workspace: Workspace,
) -> None:
    runner, story, instructions, wt_base = _setup_runner(tmp_workspace)
    runner.run("cleanup-done", story, instructions, wt_base)
    assert not (wt_base / "cleanup-done").exists()


def test_task_lifecycle_worktree_cleaned_up_on_failure(
    tmp_workspace: Workspace,
) -> None:
    runner, story, instructions, wt_base = _setup_runner(
        tmp_workspace, gates_pass=False
    )
    runner.run("cleanup-fail", story, instructions, wt_base)
    assert not (wt_base / "cleanup-fail").exists()


def test_task_lifecycle_run_yaml_has_mandatory_fields(
    tmp_workspace: Workspace,
) -> None:
    runner, story, instructions, wt_base = _setup_runner(tmp_workspace)
    runner.run("fields-task", story, instructions, wt_base)

    run_yaml = tmp_workspace.root / "_hpnc" / "runs" / "test" / "run.yaml"
    assert run_yaml.exists()
    data = yaml.safe_load(run_yaml.read_text())
    mandatory = {
        "status", "executor", "reviewer", "branch",
        "started", "finished", "files_changed", "story_source",
    }
    assert mandatory.issubset(data.keys()), f"Missing: {mandatory - data.keys()}"
