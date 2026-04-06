"""Secrets verification gate (FR57).

Checks that a pre-commit hook for secrets detection is configured.
This is a pre-flight check, not a subprocess execution.
"""

from __future__ import annotations

from pathlib import Path

from hpnc.gates.runner import GateResult

__all__ = ["SecretsGate"]

_KNOWN_HOOKS: frozenset[str] = frozenset({"git-secrets", "gitleaks"})
"""Known secrets detection pre-commit hooks."""


class SecretsGate:
    """Verifies that a secrets pre-commit hook is configured.

    Checks for .pre-commit-config.yaml containing git-secrets or gitleaks.
    """

    @property
    def name(self) -> str:
        """Gate identifier."""
        return "secrets"

    def run(self, worktree: Path) -> GateResult:
        """Check for secrets pre-commit hook in worktree.

        Args:
            worktree: Path to the Git worktree to verify.

        Returns:
            GateResult — pass if a known secrets hook is configured.
        """
        config_path = worktree / ".pre-commit-config.yaml"
        if not config_path.exists():
            return GateResult(
                name=self.name,
                passed=False,
                exit_code=1,
                stderr="No .pre-commit-config.yaml found in worktree",
            )

        content = config_path.read_text(encoding="utf-8")
        for hook in _KNOWN_HOOKS:
            if hook in content:
                return GateResult(
                    name=self.name,
                    passed=True,
                    exit_code=0,
                    stdout=f"Found secrets hook: {hook}",
                )

        return GateResult(
            name=self.name,
            passed=False,
            exit_code=1,
            stderr=f"No secrets pre-commit hook found. Expected one of: {', '.join(sorted(_KNOWN_HOOKS))}",
        )
