"""Tests for hpnc init command."""

import io
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from hpnc.cli.init_cmd import run_init


def _make_console() -> Console:
    """Create a Console that writes to a StringIO buffer."""
    return Console(file=io.StringIO(), force_terminal=False)


def _get_output(console: Console) -> str:
    """Get output from a StringIO-backed Console."""
    console.file.seek(0)  # type: ignore[union-attr]
    return console.file.read()  # type: ignore[union-attr]


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_creates_hpnc_directory(mock_run: object, tmp_path: Path) -> None:
    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    assert (tmp_path / "_hpnc").is_dir()
    assert (tmp_path / "_hpnc" / "config.yaml").is_file()
    assert (tmp_path / "_hpnc" / "executor-instructions.md").is_file()
    assert (tmp_path / "_hpnc" / "night-queue.yaml").is_file()


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_config_has_project_name(mock_run: object, tmp_path: Path) -> None:
    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    content = (tmp_path / "_hpnc" / "config.yaml").read_text()
    assert "project_name:" in content
    assert tmp_path.name in content


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_preserves_existing_config(mock_run: object, tmp_path: Path) -> None:
    hpnc_dir = tmp_path / "_hpnc"
    hpnc_dir.mkdir()
    config = hpnc_dir / "config.yaml"
    config.write_text("project_name: original\ncustom: value\n")

    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    content = config.read_text()
    assert "original" in content
    assert "custom: value" in content


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_executor_instructions_template(mock_run: object, tmp_path: Path) -> None:
    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    content = (tmp_path / "_hpnc" / "executor-instructions.md").read_text()
    assert "Executor Instructions" in content
    assert "Rules" in content


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_connectivity_missing_cli_warns(mock_run: object, tmp_path: Path) -> None:
    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    output = _get_output(console)
    assert "not found" in output


@patch("hpnc.cli.init_cmd.subprocess.run", side_effect=FileNotFoundError)
def test_init_detects_bmad(mock_run: object, tmp_path: Path) -> None:
    (tmp_path / "_bmad").mkdir()

    console = _make_console()
    run_init(project_root=tmp_path, console=console)

    output = _get_output(console)
    assert "BMAD" in output
