"""Tests for MockAgentExecutor."""

import subprocess
from pathlib import Path

from hpnc.agents.base import AgentExecutor, ExitStatus
from hpnc.agents.mock import MockAgentExecutor
from hpnc.infra.config import Config


def _make_config(tmp_path: Path) -> Config:
    """Create a minimal Config for testing."""
    return Config(project_name="test", project_root=tmp_path)


def _make_story(tmp_path: Path) -> Path:
    """Create a minimal story file for testing."""
    story = tmp_path / "story.md"
    story.write_text("# Test Story\n")
    return story


def _make_instructions(tmp_path: Path) -> Path:
    """Create a minimal instructions file for testing."""
    instructions = tmp_path / "instructions.md"
    instructions.write_text("# Instructions\n")
    return instructions


def test_mock_executor_default_config_returns_success(tmp_path: Path) -> None:
    executor = MockAgentExecutor()
    process = executor.start(
        _make_story(tmp_path), _make_config(tmp_path), _make_instructions(tmp_path)
    )
    status = executor.get_exit_status(process)
    assert status == ExitStatus.SUCCESS


def test_mock_executor_failure_config_returns_failure(tmp_path: Path) -> None:
    executor = MockAgentExecutor(default_status=ExitStatus.FAILURE)
    process = executor.start(
        _make_story(tmp_path), _make_config(tmp_path), _make_instructions(tmp_path)
    )
    status = executor.get_exit_status(process)
    assert status == ExitStatus.FAILURE


def test_mock_executor_timeout_config_returns_timeout(tmp_path: Path) -> None:
    executor = MockAgentExecutor(default_status=ExitStatus.TIMEOUT)
    process = executor.start(
        _make_story(tmp_path), _make_config(tmp_path), _make_instructions(tmp_path)
    )
    status = executor.get_exit_status(process)
    assert status == ExitStatus.TIMEOUT


def test_mock_executor_writes_simulated_files(tmp_path: Path) -> None:
    executor = MockAgentExecutor(file_changes=["output.py", "sub/nested.py"])
    story = _make_story(tmp_path)
    process = executor.start(
        story, _make_config(tmp_path), _make_instructions(tmp_path)
    )
    executor.get_exit_status(process)

    assert (tmp_path / "output.py").exists()
    assert (tmp_path / "sub" / "nested.py").exists()
    assert "Mock generated" in (tmp_path / "output.py").read_text()


def test_mock_executor_stream_output_yields_lines(tmp_path: Path) -> None:
    executor = MockAgentExecutor()
    process = executor.start(
        _make_story(tmp_path), _make_config(tmp_path), _make_instructions(tmp_path)
    )
    lines = list(executor.stream_output(process))
    assert len(lines) >= 1
    assert any("[mock]" in line for line in lines)


def test_mock_executor_satisfies_agent_executor_protocol() -> None:
    executor = MockAgentExecutor()
    assert isinstance(executor, AgentExecutor)


def test_mock_executor_start_returns_popen(tmp_path: Path) -> None:
    executor = MockAgentExecutor()
    process = executor.start(
        _make_story(tmp_path), _make_config(tmp_path), _make_instructions(tmp_path)
    )
    assert isinstance(process, subprocess.Popen)
    process.wait()
