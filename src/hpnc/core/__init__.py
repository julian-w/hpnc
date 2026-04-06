"""Core business logic for HPNC — framework-independent."""

from hpnc.core.state_machine import TERMINAL_STATES, TRANSITIONS, TaskState, transition

__all__ = ["TaskState", "TRANSITIONS", "TERMINAL_STATES", "transition"]
