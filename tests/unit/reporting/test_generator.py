"""Tests for Report Generator."""

from pathlib import Path

import yaml

from hpnc.infra.workspace import Workspace
from hpnc.reporting.generator import NightReport, ReportGenerator, TaskReport


def _create_run_yaml(run_dir: Path, data: dict[str, object]) -> None:
    """Create a run.yaml in the given directory."""
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.yaml").write_text(yaml.dump(data), encoding="utf-8")


def test_generate_report_from_run_dir(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path)
    runs_dir = tmp_path / "runs"
    reports_dir = tmp_path / "reports"

    _create_run_yaml(runs_dir / "test" / "task-a", {
        "status": "done", "executor": "opus", "reviewer": "codex",
        "started": "2026-04-06T23:00:00", "finished": "2026-04-06T23:15:00",
    })
    _create_run_yaml(runs_dir / "test" / "task-b", {
        "status": "failed", "executor": "opus", "reviewer": "codex",
    })

    gen = ReportGenerator(workspace=ws, runs_dir=runs_dir, reports_dir=reports_dir)
    report = gen.generate_from_dir(runs_dir / "test")
    assert len(report.tasks) == 2
    assert report.done_count == 1
    assert report.failed_count == 1


def test_blocked_task_has_reason_and_action(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path)
    runs_dir = tmp_path / "runs"
    reports_dir = tmp_path / "reports"

    _create_run_yaml(runs_dir / "test" / "blocked-task", {
        "status": "blocked", "block_reason": "Agent needs clarification",
    })

    gen = ReportGenerator(workspace=ws, runs_dir=runs_dir, reports_dir=reports_dir)
    report = gen.generate_from_dir(runs_dir / "test")
    task = report.tasks[0]
    assert task.status == "blocked"
    assert "clarification" in task.failure_reason
    assert task.recommended_action.startswith("->")


def test_failed_task_has_gate_details(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path)
    runs_dir = tmp_path / "runs"
    reports_dir = tmp_path / "reports"

    _create_run_yaml(runs_dir / "test" / "fail-task", {
        "status": "failed", "failure_reason": "Gate 'tests' failed: exit code 1",
    })

    gen = ReportGenerator(workspace=ws, runs_dir=runs_dir, reports_dir=reports_dir)
    report = gen.generate_from_dir(runs_dir / "test")
    task = report.tasks[0]
    assert task.status == "failed"
    assert "tests" in task.failure_reason
    assert task.recommended_action.startswith("->")


def test_markdown_report_formatting(tmp_path: Path) -> None:
    report = NightReport(
        run_date="2026-04-06",
        tasks=[
            TaskReport(name="task-a", status="done", executor="opus", reviewer="codex"),
            TaskReport(name="task-b", status="failed", executor="opus", reviewer="codex",
                       failure_reason="Lint failed", recommended_action="-> Fix lint errors"),
        ],
    )
    ws = Workspace(root=tmp_path)
    gen = ReportGenerator(workspace=ws, runs_dir=tmp_path, reports_dir=tmp_path)
    md = gen.to_markdown(report)
    assert "# Night Run Report" in md
    assert "| task-a | done |" in md
    assert "## Failed: task-b" in md
    assert "-> Fix lint errors" in md


def test_no_runs_found(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path)
    gen = ReportGenerator(workspace=ws, runs_dir=tmp_path / "empty", reports_dir=tmp_path)
    assert gen.find_latest_run() is None


def test_save_report(tmp_path: Path) -> None:
    report = NightReport(run_date="test", tasks=[])
    ws = Workspace(root=tmp_path)
    gen = ReportGenerator(workspace=ws, runs_dir=tmp_path, reports_dir=tmp_path / "reports")
    path = gen.save_report(report, "# Test\n")
    assert path.exists()
    assert "Test" in path.read_text()
