"""Night-ready frontmatter schema definition (FR16).

Defines the machine-readable fields that control task scheduling,
agent routing, and quality gate selection.
"""

from __future__ import annotations

from dataclasses import dataclass, field

__all__ = [
    "FrontmatterSchema",
    "KNOWN_GATES",
    "KNOWN_EXECUTORS",
    "MANDATORY_FIELDS",
]


@dataclass
class FrontmatterSchema:
    """Night-ready story frontmatter fields.

    Args:
        night_ready: Master switch — must be true for overnight execution.
        executor: Which agent implements (e.g., "opus", "codex").
        reviewer: Which agent reviews (e.g., "codex", "opus").
        risk: Risk level — "low", "medium", or "high".
        tests_required: Whether tests must be defined for this task.
        touches: Abstract resource names this task affects.
        blocking_questions: Must be empty for night-ready status.
        gates_required: Which quality gates to run (e.g., ["build", "tests", "lint"]).
    """

    night_ready: bool = False
    executor: str = ""
    reviewer: str = ""
    risk: str = "low"
    tests_required: bool = True
    touches: list[str] = field(default_factory=list)
    blocking_questions: list[str] = field(default_factory=list)
    gates_required: list[str] = field(default_factory=list)

    # TODO(phase-2): depends_on, release_policy, merge_policy, priority


KNOWN_GATES: frozenset[str] = frozenset({"build", "tests", "lint"})
"""Phase 1 gate names. Phase 2 adds storybook, a11y, playwright, etc."""

KNOWN_EXECUTORS: frozenset[str] = frozenset({"opus", "codex", "mock"})
"""Known agent executor identifiers."""

MANDATORY_FIELDS: frozenset[str] = frozenset({
    "night_ready",
    "executor",
    "reviewer",
    "tests_required",
    "gates_required",
})
"""Fields required for night-ready validation."""
