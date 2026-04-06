"""Tests for hpnc CLI app — command registration and help."""

from typer.testing import CliRunner

from hpnc.cli.app import app

runner = CliRunner()


def test_app_help_shows_all_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "validate" in result.output
    assert "start" in result.output
    assert "status" in result.output
    assert "queue" in result.output


def test_app_version_accessible() -> None:
    """Verify the app can be imported and has a name."""
    assert app.info.name == "hpnc"


def test_init_help() -> None:
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize" in result.output


def test_start_help() -> None:
    result = runner.invoke(app, ["start", "--help"])
    assert result.exit_code == 0
    assert "--mock" in result.output
    assert "--dry-run" in result.output
    assert "--at" in result.output
    assert "--delay" in result.output
