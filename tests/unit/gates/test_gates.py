"""Tests for individual quality gate implementations."""

import subprocess
from pathlib import Path
from unittest.mock import patch

from hpnc.gates.build import BuildGate
from hpnc.gates.lint import LintGate
from hpnc.gates.runner import Gate
from hpnc.gates.secrets import SecretsGate
from hpnc.gates.tests import TestGate


def _mock_completed(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


# --- BuildGate ---


@patch("hpnc.gates.build.subprocess.run")
def test_build_gate_pass_on_zero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(0, stdout="OK")  # type: ignore[union-attr]
    gate = BuildGate()
    result = gate.run(Path("/fake"))
    assert result.passed is True
    assert result.exit_code == 0


@patch("hpnc.gates.build.subprocess.run")
def test_build_gate_fail_on_nonzero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(1, stderr="SyntaxError")  # type: ignore[union-attr]
    gate = BuildGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False
    assert result.exit_code == 1
    assert "SyntaxError" in result.stderr


# --- TestGate ---


@patch("hpnc.gates.tests.subprocess.run")
def test_test_gate_pass_on_zero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(0, stdout="5 passed")  # type: ignore[union-attr]
    gate = TestGate()
    result = gate.run(Path("/fake"))
    assert result.passed is True


@patch("hpnc.gates.tests.subprocess.run")
def test_test_gate_fail_on_nonzero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(1, stderr="FAILED")  # type: ignore[union-attr]
    gate = TestGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False


# --- LintGate ---


@patch("hpnc.gates.lint.subprocess.run")
def test_lint_gate_pass_on_zero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(0)  # type: ignore[union-attr]
    gate = LintGate()
    result = gate.run(Path("/fake"))
    assert result.passed is True


@patch("hpnc.gates.lint.subprocess.run")
def test_lint_gate_fail_on_nonzero_exit(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(1, stderr="E501 line too long")  # type: ignore[union-attr]
    gate = LintGate()
    result = gate.run(Path("/fake"))
    assert result.passed is False
    assert "E501" in result.stderr


# --- SecretsGate ---


def test_secrets_gate_pass_with_hook_present(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n      - id: gitleaks\n"
    )
    gate = SecretsGate()
    result = gate.run(tmp_path)
    assert result.passed is True
    assert "gitleaks" in result.stdout


def test_secrets_gate_fail_without_hook(tmp_path: Path) -> None:
    gate = SecretsGate()
    result = gate.run(tmp_path)
    assert result.passed is False
    assert "No .pre-commit-config.yaml" in result.stderr


def test_secrets_gate_fail_without_known_hook(tmp_path: Path) -> None:
    (tmp_path / ".pre-commit-config.yaml").write_text(
        "repos:\n  - repo: local\n    hooks:\n      - id: ruff\n"
    )
    gate = SecretsGate()
    result = gate.run(tmp_path)
    assert result.passed is False
    assert "No secrets pre-commit hook found" in result.stderr


# --- Diagnostic fields ---


@patch("hpnc.gates.build.subprocess.run")
def test_gate_result_includes_name_exitcode_stderr(mock_run: object) -> None:
    mock_run.return_value = _mock_completed(2, stderr="fatal error")  # type: ignore[union-attr]
    gate = BuildGate()
    result = gate.run(Path("/fake"))
    assert result.name == "build"
    assert result.exit_code == 2
    assert result.stderr == "fatal error"


# --- Protocol conformance ---


def test_gate_satisfies_protocol() -> None:
    assert isinstance(BuildGate(), Gate)
    assert isinstance(TestGate(), Gate)
    assert isinstance(LintGate(), Gate)
    assert isinstance(SecretsGate(), Gate)
