"""Tests for hpnc validate CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from hpnc.cli.app import app

runner = CliRunner()


def test_validate_no_project_fails() -> None:
    """validate without hpnc project should fail."""
    result = runner.invoke(app, ["validate"])
    assert result.exit_code != 0


def test_validate_empty_queue_fails(tmp_path: Path) -> None:
    """validate with empty queue should report issues."""
    import os

    hpnc_dir = tmp_path / "_hpnc"
    hpnc_dir.mkdir()
    (hpnc_dir / "config.yaml").write_text("project_name: test\n")
    (hpnc_dir / "night-queue.yaml").write_text("tasks: []\n")

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        result = runner.invoke(app, ["validate"])
        assert result.exit_code != 0
    finally:
        os.chdir(old_cwd)
