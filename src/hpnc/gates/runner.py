"""Gate orchestration — Protocol, results, and sequential runner.

Gates verify code quality after agent implementation. GateRunner executes
all gates sequentially (never short-circuits) and returns aggregated results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

__all__ = ["GateResult", "GateResults", "Gate", "GateRunner"]


@dataclass
class GateResult:
    """Result of a single gate execution.

    Args:
        name: Gate identifier (e.g., "build", "tests", "lint").
        passed: True only when subprocess exit code is 0 (NFR7).
        exit_code: The subprocess exit code.
        stdout: Captured standard output.
        stderr: Captured standard error (for diagnosis on failure).
    """

    name: str
    passed: bool
    exit_code: int
    stdout: str = ""
    stderr: str = ""


@dataclass
class GateResults:
    """Aggregated results from all gate executions.

    Args:
        results: List of individual gate results.
    """

    results: list[GateResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True only when ALL gates passed (NFR7).

        Returns True for empty results (vacuous truth).
        """
        return all(r.passed for r in self.results)


@runtime_checkable
class Gate(Protocol):
    """Protocol for quality gate implementations.

    Each gate runs a verification step against a worktree and
    returns a structured result.
    """

    @property
    def name(self) -> str:
        """Gate identifier."""
        ...

    def run(self, worktree: Path) -> GateResult:
        """Execute the gate against a worktree.

        Args:
            worktree: Path to the Git worktree to verify.

        Returns:
            GateResult with pass/fail status and diagnostic output.
        """
        ...


class GateRunner:
    """Executes all gates sequentially and collects results.

    Never short-circuits — all gates execute even if the first fails,
    giving a complete picture for the morning report.

    Args:
        gates: List of Gate implementations to execute.
    """

    def __init__(self, gates: list[Gate]) -> None:
        self.gates = gates

    def run_all(self, worktree: Path) -> GateResults:
        """Execute all gates against the worktree.

        Args:
            worktree: Path to the Git worktree to verify.

        Returns:
            Aggregated results from all gates.
        """
        results = GateResults()
        for gate in self.gates:
            result = gate.run(worktree)
            results.results.append(result)
        return results
