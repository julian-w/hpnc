"""hpnc validate — pre-flight validation command (FR18, NFR15)."""

from __future__ import annotations

import typer
from rich.console import Console

from hpnc.core.queue_manager import QueueManager
from hpnc.core.validator import Validator
from hpnc.infra.config import CONFIG_DIR, ConfigLoader
from hpnc.infra.errors import HpncError
from hpnc.infra.workspace import Workspace


def validate() -> None:
    """Run pre-flight validation checks."""
    console = Console()

    try:
        loader = ConfigLoader()
        root = loader.find_root()
        workspace = Workspace(root=root)
        queue_path = root / CONFIG_DIR / "night-queue.yaml"
        manager = QueueManager(workspace=workspace, queue_path=queue_path)
        tasks = manager.list_tasks()

        validator = Validator(project_root=root)
        result = validator.validate_queue(tasks)

        if result.passed:
            console.print(
                f"\n[bold green]Validation passed[/bold green] — "
                f"{len(tasks)} story(ies) ready for night run"
            )
            raise typer.Exit(code=0)

        console.print(f"\n[bold red]Validation failed[/bold red] — {len(result.issues)} issue(s):\n")
        for issue in result.issues:
            console.print(f"  [red]✗[/red] [{issue.story}] {issue.what}")
            console.print(f"    Why: {issue.why}")
            console.print(f"    Fix: {issue.action}\n")
        raise typer.Exit(code=1)

    except HpncError as e:
        console.print(f"\n[red]✗[/red] {e}")
        raise typer.Exit(code=e.exit_code) from e
