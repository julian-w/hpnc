"""Pure state machine for task lifecycle — no I/O, no side effects.

Receives current state and target state, returns new state or raises.
"""

from __future__ import annotations

from enum import Enum

from hpnc.infra.errors import InvalidTransitionError

__all__ = ["TaskState", "TRANSITIONS", "TERMINAL_STATES", "transition"]


class TaskState(Enum):
    """All task lifecycle states (Phase 1 + Phase 2 labels)."""

    # Phase 1 States
    QUEUED = "queued"
    SETUP_WORKTREE = "setup_worktree"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    GATES = "gates"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"

    # Phase 2 States (defined now, transitions added later)
    FIX_ATTEMPT = "fix_attempt"
    PAUSED = "paused"
    AWAITING_REVIEW = "awaiting_review"
    PROPOSAL = "proposal"
    MERGED = "merged"
    INTERRUPTED = "interrupted"


TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.QUEUED: [TaskState.SETUP_WORKTREE],
    TaskState.SETUP_WORKTREE: [TaskState.IMPLEMENTATION, TaskState.FAILED],
    TaskState.IMPLEMENTATION: [TaskState.REVIEW, TaskState.BLOCKED],
    TaskState.REVIEW: [TaskState.GATES, TaskState.BLOCKED],
    TaskState.GATES: [TaskState.DONE, TaskState.FAILED],
}
"""Phase 1 transition table. Phase 2 transitions will be added later."""

TERMINAL_STATES: frozenset[TaskState] = frozenset(
    {TaskState.DONE, TaskState.FAILED, TaskState.BLOCKED}
)
"""States that cannot transition further."""


def transition(current: TaskState, target: TaskState) -> TaskState:
    """Transition from current state to target state.

    Args:
        current: The current task state.
        target: The desired next state.

    Returns:
        The target state if the transition is valid.

    Raises:
        InvalidTransitionError: If the transition is not allowed.
    """
    if current in TERMINAL_STATES:
        raise InvalidTransitionError(
            what=f"Cannot transition from terminal state '{current.value}'",
            why=f"State '{current.value}' is a terminal state and does not allow further transitions",
            action="Check task state before attempting transition",
        )

    allowed = TRANSITIONS.get(current)
    if allowed is None or target not in allowed:
        raise InvalidTransitionError(
            what=f"Invalid transition: '{current.value}' -> '{target.value}'",
            why=f"Allowed transitions from '{current.value}': {[s.value for s in (allowed or [])]}",
            action="Use only valid transitions as defined in the transition table",
        )

    return target
