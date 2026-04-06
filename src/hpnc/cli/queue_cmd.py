"""hpnc queue — night queue management commands."""

from typing import Annotated

import typer

queue_app = typer.Typer(help="Manage the night queue.")


@queue_app.command()
def add(
    story: Annotated[str, typer.Argument(help="Path to story file")],
) -> None:
    """Add a story to the night queue."""
    typer.echo(f"Not yet implemented: hpnc queue add {story}")
