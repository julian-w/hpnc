"""HPNC CLI application — Typer-based command interface."""

import typer

from hpnc.cli.init_cmd import run_init
from hpnc.cli.queue_cmd import queue_app
from hpnc.cli.start_cmd import start
from hpnc.cli.status_cmd import status
from hpnc.cli.validate_cmd import validate

app = typer.Typer(
    name="hpnc",
    help="Human-Planned Night Crew — overnight AI task automation.",
)


@app.command()
def init() -> None:
    """Initialize HPNC in the current project."""
    run_init()


app.command()(validate)
app.command()(start)
app.command()(status)
app.add_typer(queue_app, name="queue")


def main() -> None:
    """Entry point for hpnc CLI."""
    app()
