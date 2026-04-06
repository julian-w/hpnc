"""Report Generator — morning report from night run artifacts (FR59-FR62).

Generates markdown reports and Rich-formatted terminal output.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hpnc.infra.workspace import Workspace

__all__ = ["ReportGenerator", "TaskReport"]


@dataclass
class TaskReport:
    """Summary of a single task's run result.

    Args:
        name: Task name.
        status: Terminal status (done/failed/blocked).
        executor: Executor agent name.
        reviewer: Reviewer agent name.
        started: ISO timestamp.
        finished: ISO timestamp.
        story_source: Path to story file.
        failure_reason: Why it failed (gate name, stderr excerpt).
        recommended_action: What to do next.
    """

    name: str
    status: str
    executor: str = ""
    reviewer: str = ""
    started: str = ""
    finished: str = ""
    story_source: str = ""
    failure_reason: str = ""
    recommended_action: str = ""


@dataclass
class NightReport:
    """Aggregated night run report.

    Args:
        run_date: Date of the run.
        tasks: List of task reports.
    """

    run_date: str
    tasks: list[TaskReport] = field(default_factory=list)

    @property
    def done_count(self) -> int:
        """Number of tasks with done status."""
        return sum(1 for t in self.tasks if t.status == "done")

    @property
    def failed_count(self) -> int:
        """Number of tasks with failed status."""
        return sum(1 for t in self.tasks if t.status == "failed")

    @property
    def blocked_count(self) -> int:
        """Number of tasks with blocked status."""
        return sum(1 for t in self.tasks if t.status == "blocked")


class ReportGenerator:
    """Generates morning reports from night run artifacts.

    Args:
        workspace: Workspace for reading run artifacts.
        runs_dir: Base directory for run artifacts.
        reports_dir: Directory to save generated reports.
    """

    def __init__(
        self, workspace: Workspace, runs_dir: Path, reports_dir: Path
    ) -> None:
        self.workspace = workspace
        self.runs_dir = runs_dir
        self.reports_dir = reports_dir

    def find_latest_run(self) -> Path | None:
        """Find the most recent run directory.

        Returns:
            Path to latest run dir, or None if no runs exist.
        """
        if not self.runs_dir.exists():
            return None

        run_dirs = sorted(
            [d for d in self.runs_dir.rglob("run.yaml")],
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not run_dirs:
            return None
        return run_dirs[0].parent

    def generate_from_dir(self, run_dir: Path) -> NightReport:
        """Generate a report from a run directory containing run.yaml files.

        Args:
            run_dir: Directory containing task subdirs with run.yaml.

        Returns:
            NightReport with all task results.
        """
        report = NightReport(run_date=run_dir.name)

        # Check if run_dir itself has run.yaml (single task)
        # or subdirs have run.yaml (multiple tasks from dispatcher)
        run_yaml = run_dir / "run.yaml"
        if run_yaml.exists():
            task_report = self._parse_run_yaml(run_dir.name, run_yaml)
            report.tasks.append(task_report)
        else:
            for subdir in sorted(run_dir.iterdir()):
                sub_yaml = subdir / "run.yaml"
                if subdir.is_dir() and sub_yaml.exists():
                    task_report = self._parse_run_yaml(subdir.name, sub_yaml)
                    report.tasks.append(task_report)

        return report

    def _parse_run_yaml(self, task_name: str, yaml_path: Path) -> TaskReport:
        """Parse a run.yaml into a TaskReport.

        Args:
            task_name: Name of the task.
            yaml_path: Path to run.yaml.

        Returns:
            Parsed TaskReport.
        """
        data: dict[str, Any] = self.workspace.read_yaml(yaml_path)

        status = str(data.get("status", "unknown"))
        failure_reason = ""
        recommended_action = ""

        if status == "failed":
            failure_reason = str(data.get("failure_reason", "Quality gate(s) failed"))
            recommended_action = "-> Review gate output and fix issues"
        elif status == "blocked":
            failure_reason = str(data.get("block_reason", "Agent could not proceed"))
            recommended_action = "-> Review story requirements and unblock manually"

        return TaskReport(
            name=task_name,
            status=status,
            executor=str(data.get("executor", "")),
            reviewer=str(data.get("reviewer", "")),
            started=str(data.get("started", "")),
            finished=str(data.get("finished", "")),
            story_source=str(data.get("story_source", "")),
            failure_reason=failure_reason,
            recommended_action=recommended_action,
        )

    def to_markdown(self, report: NightReport) -> str:
        """Generate markdown report text.

        Args:
            report: The night report to format.

        Returns:
            Markdown-formatted report string.
        """
        lines = [
            f"# Night Run Report — {report.run_date}",
            "",
            f"**Tasks:** {len(report.tasks)} "
            f"({report.done_count} done, {report.failed_count} failed, "
            f"{report.blocked_count} blocked)",
            "",
            "| Task | Status | Executor | Reviewer |",
            "|------|--------|----------|----------|",
        ]

        for t in report.tasks:
            lines.append(f"| {t.name} | {t.status} | {t.executor} | {t.reviewer} |")

        # Detail sections for non-done tasks
        for t in report.tasks:
            if t.status == "failed":
                lines.extend([
                    "",
                    f"## Failed: {t.name}",
                    f"**Reason:** {t.failure_reason}",
                    f"{t.recommended_action}",
                ])
            elif t.status == "blocked":
                lines.extend([
                    "",
                    f"## Blocked: {t.name}",
                    f"**Reason:** {t.failure_reason}",
                    f"{t.recommended_action}",
                ])

        lines.append("")
        return "\n".join(lines)

    def save_report(self, report: NightReport, markdown: str) -> Path:
        """Save a markdown report to the reports directory.

        Args:
            report: The night report.
            markdown: Markdown text to save.

        Returns:
            Path to the saved report file.
        """
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.reports_dir / f"{report.run_date}-report.md"
        report_path.write_text(markdown, encoding="utf-8")
        return report_path
