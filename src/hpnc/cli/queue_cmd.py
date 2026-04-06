"""hpnc queue — night queue management commands."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from hpnc.core.queue_manager import QueueManager, parse_frontmatter
from hpnc.infra.config import CONFIG_DIR, ConfigLoader
from hpnc.infra.errors import HpncError
from hpnc.infra.workspace import Workspace

queue_app = typer.Typer(help="Manage the night queue.")


@queue_app.command()
def add(
    story: Annotated[str, typer.Argument(help="Path to story file")],
) -> None:
    """Add a story to the night queue."""
    console = Console()
    story_path = Path(story)

    try:
        loader = ConfigLoader()
        root = loader.find_root()
        workspace = Workspace(root=root)
        queue_path = root / CONFIG_DIR / "night-queue.yaml"
        manager = QueueManager(workspace=workspace, queue_path=queue_path)

        added = manager.add(story_path)

        if added:
            fm = parse_frontmatter(story_path.resolve())
            console.print(f"\n[green]✓[/green] Added to queue: {story_path}")
            console.print(f"  executor: {fm.executor or 'default'}")
            console.print(f"  reviewer: {fm.reviewer or 'default'}")
            console.print(f"  night_ready: {fm.night_ready}")
        else:
            console.print(f"\n[yellow]![/yellow] Already in queue: {story_path}")

    except HpncError as e:
        console.print(f"\n[red]✗[/red] {e}")
        raise typer.Exit(code=e.exit_code) from e
