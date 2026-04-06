"""Tests for hpnc queue CLI commands."""


from typer.testing import CliRunner

from hpnc.cli.app import app

runner = CliRunner()


def test_queue_add_no_project_fails() -> None:
    """queue add without hpnc project should fail."""
    result = runner.invoke(app, ["queue", "add", "story.md"])
    assert result.exit_code != 0
