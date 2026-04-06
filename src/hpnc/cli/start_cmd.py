"""hpnc start — night run execution command."""

from typing import Annotated

import typer


def start(
    at: Annotated[str | None, typer.Option(help="Schedule start time (e.g. 23:00)")] = None,
    delay: Annotated[str | None, typer.Option(help="Delay before start (e.g. 30m)")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Simulate without executing agents")] = False,
    mock: Annotated[bool, typer.Option("--mock", help="Use mock agents instead of real ones")] = False,
) -> None:
    """Start a night run."""
    typer.echo("Not yet implemented: hpnc start")
