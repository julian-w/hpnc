"""hpnc status — morning review command (FR59-FR62)."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from hpnc.infra.config import CONFIG_DIR, ConfigLoader
from hpnc.infra.errors import HpncError
from hpnc.infra.workspace import Workspace
from hpnc.reporting.generator import ReportGenerator


def status() -> None:
    """Show morning report — what happened last night."""
    console = Console()

    try:
        loader = ConfigLoader()
        root = loader.find_root()
        workspace = Workspace(root=root)

        runs_dir = root / CONFIG_DIR / "runs"
        reports_dir = root / CONFIG_DIR / "reports"
        gen = ReportGenerator(
            workspace=workspace, runs_dir=runs_dir, reports_dir=reports_dir
        )

        latest = gen.find_latest_run()
        if latest is None:
            console.print("\n[dim]No night run results found.[/dim]")
            console.print("  Run 'hpnc start --mock' to execute a night run.")
            raise typer.Exit(code=0)

        report = gen.generate_from_dir(latest)

        # Rich table
        table = Table(title=f"Night Run — {report.run_date}")
        table.add_column("Task", style="bold")
        table.add_column("Status")
        table.add_column("Executor")
        table.add_column("Reviewer")

        for t in report.tasks:
            status_style = {
                "done": "[green]done[/green]",
                "failed": "[red]failed[/red]",
                "blocked": "[yellow]blocked[/yellow]",
            }.get(t.status, t.status)
            table.add_row(t.name, status_style, t.executor, t.reviewer)

        console.print()
        console.print(table)

        # Details for failed/blocked
        for t in report.tasks:
            if t.status in {"failed", "blocked"}:
                color = "red" if t.status == "failed" else "yellow"
                console.print(f"\n[{color}]{t.status.upper()}: {t.name}[/{color}]")
                console.print(f"  {t.failure_reason}")
                console.print(f"  {t.recommended_action}")

        console.print(
            f"\n[bold]{report.done_count} done, "
            f"{report.failed_count} failed, "
            f"{report.blocked_count} blocked[/bold]"
        )

        # Save markdown report
        markdown = gen.to_markdown(report)
        report_path = gen.save_report(report, markdown)
        console.print(f"\n  Report saved: {report_path}")

    except HpncError as e:
        console.print(f"\n[red]✗[/red] {e}")
        raise typer.Exit(code=e.exit_code) from e
