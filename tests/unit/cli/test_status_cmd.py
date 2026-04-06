"""Tests for hpnc status CLI command."""

from pathlib import Path

from typer.testing import CliRunner

from hpnc.cli.app import app

runner = CliRunner()


def test_status_no_project_fails() -> None:
    """status without hpnc project should fail."""
    result = runner.invoke(app, ["status"])
    assert result.exit_code != 0


def test_status_no_runs_exits_clean(tmp_path: Path) -> None:
    """status with no runs should show message and exit 0."""
    import os

    hpnc_dir = tmp_path / "_hpnc"
    hpnc_dir.mkdir()
    (hpnc_dir / "config.yaml").write_text("project_name: test\n")

    old_cwd = os.getcwd()
    try:
        os.chdir(str(tmp_path))
        result = runner.invoke(app, ["status"])
        assert result.exit_code == 0
        assert "No night run" in result.output or "no" in result.output.lower()
    finally:
        os.chdir(old_cwd)
