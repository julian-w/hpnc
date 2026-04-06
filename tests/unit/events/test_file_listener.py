"""Tests for FileEventListener."""

from pathlib import Path

import yaml

from hpnc.core.state_machine import TaskState
from hpnc.events.base import RunResult, TaskEventListener
from hpnc.events.file_listener import FileEventListener
from hpnc.infra.workspace import Workspace


def test_file_listener_on_status_change_writes_yaml(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "001"
    ws = Workspace(root=tmp_path)
    listener = FileEventListener(run_dir=run_dir, workspace=ws)

    listener.on_status_change("login-task", TaskState.QUEUED, TaskState.SETUP_WORKTREE)

    run_yaml = run_dir / "run.yaml"
    assert run_yaml.exists()
    data = yaml.safe_load(run_yaml.read_text())
    assert data["status"] == "setup_worktree"
    assert data["previous_status"] == "queued"
    assert data["task"] == "login-task"


def test_file_listener_on_status_change_immediate_persist(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "002"
    ws = Workspace(root=tmp_path)
    listener = FileEventListener(run_dir=run_dir, workspace=ws)

    listener.on_status_change("task-a", TaskState.SETUP_WORKTREE, TaskState.IMPLEMENTATION)

    # File must exist immediately — no batching
    assert (run_dir / "run.yaml").exists()


def test_file_listener_on_complete_writes_all_fields(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "003"
    ws = Workspace(root=tmp_path)
    listener = FileEventListener(run_dir=run_dir, workspace=ws)

    result = RunResult(
        status=TaskState.DONE,
        executor="opus",
        reviewer="codex",
        branch="night/login-task",
        started="2026-04-06T23:12:00",
        finished="2026-04-06T23:36:00",
        files_changed=["src/login.py", "tests/test_login.py"],
        story_source="stories/login.md",
    )
    listener.on_complete("login-task", result)

    data = yaml.safe_load((run_dir / "run.yaml").read_text())
    assert data["status"] == "done"
    assert data["executor"] == "opus"
    assert data["reviewer"] == "codex"
    assert data["branch"] == "night/login-task"
    assert data["started"] == "2026-04-06T23:12:00"
    assert data["finished"] == "2026-04-06T23:36:00"
    assert data["files_changed"] == ["src/login.py", "tests/test_login.py"]
    assert data["story_source"] == "stories/login.md"


def test_file_listener_on_complete_mandatory_fields(tmp_path: Path) -> None:
    run_dir = tmp_path / "runs" / "004"
    ws = Workspace(root=tmp_path)
    listener = FileEventListener(run_dir=run_dir, workspace=ws)

    result = RunResult(
        status=TaskState.FAILED,
        executor="codex",
        reviewer="opus",
        branch="night/broken-task",
        started="2026-04-06T23:00:00",
        finished="2026-04-06T23:05:00",
        story_source="stories/broken.md",
    )
    listener.on_complete("broken-task", result)

    data = yaml.safe_load((run_dir / "run.yaml").read_text())
    mandatory = {"status", "executor", "reviewer", "branch", "started", "finished", "files_changed", "story_source"}
    assert mandatory.issubset(data.keys())


def test_file_listener_satisfies_protocol() -> None:
    ws = Workspace(root=Path("/fake"))
    listener = FileEventListener(run_dir=Path("/fake/runs"), workspace=ws)
    assert isinstance(listener, TaskEventListener)
