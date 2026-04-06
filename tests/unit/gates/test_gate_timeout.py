"""Tests for gate timeout handling."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from hpnc.gates.build import BuildGate
from hpnc.gates.lint import LintGate
from hpnc.gates.tests import TestGate


@patch("hpnc.gates.build.subprocess.run")
def test_build_gate_timeout_returns_failed(mock_run: object) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="build", timeout=300)  # type: ignore[union-attr]
    gate = BuildGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False
    assert "timed out" in result.stderr


@patch("hpnc.gates.tests.subprocess.run")
def test_test_gate_timeout_returns_failed(mock_run: object) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=300)  # type: ignore[union-attr]
    gate = TestGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False
    assert "timed out" in result.stderr


@patch("hpnc.gates.lint.subprocess.run")
def test_lint_gate_timeout_returns_failed(mock_run: object) -> None:
    mock_run.side_effect = subprocess.TimeoutExpired(cmd="lint", timeout=300)  # type: ignore[union-attr]
    gate = LintGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False
    assert "timed out" in result.stderr
