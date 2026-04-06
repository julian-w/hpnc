"""Tests for HPNC state machine transitions."""

import pytest

from hpnc.core.state_machine import TERMINAL_STATES, TRANSITIONS, TaskState, transition
from hpnc.infra.errors import InvalidTransitionError

# --- Valid Phase 1 transitions ---


def test_state_machine_queued_to_setup_worktree_succeeds() -> None:
    result = transition(TaskState.QUEUED, TaskState.SETUP_WORKTREE)
    assert result == TaskState.SETUP_WORKTREE


def test_state_machine_setup_worktree_to_implementation_succeeds() -> None:
    result = transition(TaskState.SETUP_WORKTREE, TaskState.IMPLEMENTATION)
    assert result == TaskState.IMPLEMENTATION


def test_state_machine_setup_worktree_to_failed_succeeds() -> None:
    result = transition(TaskState.SETUP_WORKTREE, TaskState.FAILED)
    assert result == TaskState.FAILED


def test_state_machine_implementation_to_review_succeeds() -> None:
    result = transition(TaskState.IMPLEMENTATION, TaskState.REVIEW)
    assert result == TaskState.REVIEW


def test_state_machine_implementation_to_blocked_succeeds() -> None:
    result = transition(TaskState.IMPLEMENTATION, TaskState.BLOCKED)
    assert result == TaskState.BLOCKED


def test_state_machine_review_to_gates_succeeds() -> None:
    result = transition(TaskState.REVIEW, TaskState.GATES)
    assert result == TaskState.GATES


def test_state_machine_review_to_blocked_succeeds() -> None:
    result = transition(TaskState.REVIEW, TaskState.BLOCKED)
    assert result == TaskState.BLOCKED


def test_state_machine_gates_to_done_succeeds() -> None:
    result = transition(TaskState.GATES, TaskState.DONE)
    assert result == TaskState.DONE


def test_state_machine_gates_to_failed_succeeds() -> None:
    result = transition(TaskState.GATES, TaskState.FAILED)
    assert result == TaskState.FAILED


# --- Invalid transitions ---


def test_state_machine_invalid_transition_raises() -> None:
    with pytest.raises(InvalidTransitionError):
        transition(TaskState.QUEUED, TaskState.DONE)


def test_state_machine_terminal_state_transition_raises() -> None:
    for terminal in TERMINAL_STATES:
        with pytest.raises(InvalidTransitionError):
            transition(terminal, TaskState.QUEUED)


# --- Enum completeness ---


def test_task_state_all_phase1_states_exist() -> None:
    phase1 = {
        "QUEUED", "SETUP_WORKTREE", "IMPLEMENTATION", "REVIEW",
        "GATES", "DONE", "FAILED", "BLOCKED",
    }
    members = {m.name for m in TaskState}
    assert phase1.issubset(members)


def test_task_state_all_phase2_states_exist() -> None:
    phase2 = {
        "FIX_ATTEMPT", "PAUSED", "AWAITING_REVIEW",
        "PROPOSAL", "MERGED", "INTERRUPTED",
    }
    members = {m.name for m in TaskState}
    assert phase2.issubset(members)


def test_task_state_values_are_lowercase_strings() -> None:
    for state in TaskState:
        assert state.value == state.value.lower(), (
            f"{state.name} value must be lowercase"
        )
        assert isinstance(state.value, str)


def test_transition_table_covers_all_non_terminal_phase1_states() -> None:
    """Every non-terminal Phase 1 state must have transitions defined."""
    phase1_non_terminal = {
        TaskState.QUEUED, TaskState.SETUP_WORKTREE,
        TaskState.IMPLEMENTATION, TaskState.REVIEW, TaskState.GATES,
    }
    for state in phase1_non_terminal:
        assert state in TRANSITIONS, f"{state.name} missing from TRANSITIONS"
