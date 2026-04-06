"""Tests for GateRunner orchestration logic."""

from pathlib import Path

from hpnc.gates.runner import GateResult, GateResults, GateRunner


class _PassGate:
    """Mock gate that always passes."""

    def __init__(self, gate_name: str = "mock-pass") -> None:
        self._name = gate_name

    @property
    def name(self) -> str:
        return self._name

    def run(self, worktree: Path) -> GateResult:
        return GateResult(name=self.name, passed=True, exit_code=0)


class _FailGate:
    """Mock gate that always fails."""

    def __init__(self, gate_name: str = "mock-fail") -> None:
        self._name = gate_name

    @property
    def name(self) -> str:
        return self._name

    def run(self, worktree: Path) -> GateResult:
        return GateResult(
            name=self.name, passed=False, exit_code=1, stderr="mock failure"
        )


def test_gate_runner_all_pass_returns_passed() -> None:
    runner = GateRunner(gates=[_PassGate("a"), _PassGate("b"), _PassGate("c")])  # type: ignore[list-item]
    results = runner.run_all(Path("/fake"))
    assert results.passed is True
    assert len(results.results) == 3


def test_gate_runner_one_fail_returns_not_passed() -> None:
    runner = GateRunner(gates=[_PassGate("a"), _FailGate("b"), _PassGate("c")])  # type: ignore[list-item]
    results = runner.run_all(Path("/fake"))
    assert results.passed is False


def test_gate_runner_no_short_circuit() -> None:
    runner = GateRunner(gates=[_FailGate("first"), _PassGate("second"), _FailGate("third")])  # type: ignore[list-item]
    results = runner.run_all(Path("/fake"))
    assert len(results.results) == 3
    assert results.results[0].name == "first"
    assert results.results[1].name == "second"
    assert results.results[2].name == "third"


def test_gate_runner_empty_gates_returns_passed() -> None:
    runner = GateRunner(gates=[])
    results = runner.run_all(Path("/fake"))
    assert results.passed is True
    assert len(results.results) == 0


def test_gate_results_passed_only_when_all_pass() -> None:
    all_pass = GateResults(results=[
        GateResult(name="a", passed=True, exit_code=0),
        GateResult(name="b", passed=True, exit_code=0),
    ])
    assert all_pass.passed is True

    one_fail = GateResults(results=[
        GateResult(name="a", passed=True, exit_code=0),
        GateResult(name="b", passed=False, exit_code=1),
    ])
    assert one_fail.passed is False
