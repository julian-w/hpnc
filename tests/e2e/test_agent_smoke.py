"""E2E smoke tests for real agent CLI integration.

These tests invoke real AI agents and cost tokens.
Run only when explicitly needed: pytest tests/e2e/ -v

Requires:
- Claude Code CLI installed and authenticated
- Codex CLI installed and authenticated
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from hpnc.agents.base import ExitStatus
from hpnc.agents.claude_code import ClaudeCodeExecutor
from hpnc.agents.codex import CodexExecutor
from hpnc.infra.config import Config

# Mark all tests as e2e — skip by default in CI
pytestmark = pytest.mark.e2e


def _is_cli_available(cmd: str) -> bool:
    """Check if a CLI tool is on PATH (handles Windows .cmd wrappers)."""
    found = shutil.which(cmd)
    if not found:
        return False
    try:
        result = subprocess.run(
            [found, "--version"], capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


# --- Claude Code ---


@pytest.mark.skipif(
    not _is_cli_available("claude"),
    reason="Claude Code CLI not installed",
)
def test_claude_code_connectivity() -> None:
    """Verify Claude Code CLI responds to --version."""
    ClaudeCodeExecutor.check_connectivity()


@pytest.mark.skipif(
    not _is_cli_available("claude"),
    reason="Claude Code CLI not installed",
)
def test_claude_code_simple_prompt(tmp_path: Path) -> None:
    """Invoke Claude Code with a trivial prompt and verify it completes."""
    story = tmp_path / "story.md"
    story.write_text("Respond with exactly: HPNC_TEST_OK\n")
    instructions = tmp_path / "instructions.md"
    instructions.write_text("You are a test helper. Follow instructions exactly.\n")
    config = Config(project_name="test", project_root=tmp_path)

    executor = ClaudeCodeExecutor()
    process = executor.start(story, config, instructions)
    output_lines = list(executor.stream_output(process))
    status = executor.get_exit_status(process)

    assert status == ExitStatus.SUCCESS, f"Exit code: {process.returncode}"
    output = "\n".join(output_lines)
    assert len(output) > 0, "Expected some output from Claude Code"


# --- Codex ---


@pytest.mark.skipif(
    not _is_cli_available("codex"),
    reason="Codex CLI not installed",
)
def test_codex_connectivity() -> None:
    """Verify Codex CLI responds to --version."""
    CodexExecutor.check_connectivity()


@pytest.mark.skipif(
    not _is_cli_available("codex"),
    reason="Codex CLI not installed",
)
def test_codex_simple_prompt(tmp_path: Path) -> None:
    """Invoke Codex with a trivial prompt and verify it completes."""
    # Codex requires a git repo
    subprocess.run(
        ["git", "init"], cwd=str(tmp_path),
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"],
        cwd=str(tmp_path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "T"],
        cwd=str(tmp_path), capture_output=True, check=True,
    )
    (tmp_path / "README.md").write_text("# Test\n")
    subprocess.run(
        ["git", "add", "."], cwd=str(tmp_path),
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=str(tmp_path),
        capture_output=True, check=True,
    )

    story = tmp_path / "story.md"
    story.write_text("Respond with exactly: HPNC_TEST_OK\n")
    instructions = tmp_path / "instructions.md"
    instructions.write_text("Follow instructions exactly.\n")
    config = Config(project_name="test", project_root=tmp_path)

    executor = CodexExecutor()
    process = executor.start(story, config, instructions)
    output_lines = list(executor.stream_output(process))
    status = executor.get_exit_status(process)

    stderr = process.stderr.read() if process.stderr else ""
    assert status == ExitStatus.SUCCESS, (
        f"Exit code: {process.returncode}\n"
        f"stdout: {output_lines}\n"
        f"stderr: {stderr}"
    )
