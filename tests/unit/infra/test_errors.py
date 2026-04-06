"""Tests for HPNC error hierarchy."""

from hpnc.infra.errors import (
    ConfigError,
    ConnectivityError,
    HpncError,
    InvalidTransitionError,
    TaskBlockedError,
    TaskInterruptedError,
    ValidationError,
)


def test_hpnc_error_stores_what_why_action() -> None:
    err = HpncError(what="disk full", why="no space left", action="free disk space")
    assert err.what == "disk full"
    assert err.why == "no space left"
    assert err.action == "free disk space"


def test_hpnc_error_str_format() -> None:
    err = HpncError(what="disk full", why="no space left", action="free disk space")
    result = str(err)
    assert "disk full" in result
    assert "no space left" in result
    assert "free disk space" in result
    assert "Action:" in result


def test_config_error_exit_code_is_4() -> None:
    err = ConfigError(what="x", why="y", action="z")
    assert err.exit_code == 4


def test_connectivity_error_exit_code_is_5() -> None:
    err = ConnectivityError(what="x", why="y", action="z")
    assert err.exit_code == 5


def test_validation_error_exit_code_is_1() -> None:
    err = ValidationError(what="x", why="y", action="z")
    assert err.exit_code == 1


def test_task_blocked_error_exit_code_is_2() -> None:
    err = TaskBlockedError(what="x", why="y", action="z")
    assert err.exit_code == 2


def test_task_interrupted_error_exit_code_is_3() -> None:
    err = TaskInterruptedError(what="x", why="y", action="z")
    assert err.exit_code == 3


def test_invalid_transition_error_exit_code() -> None:
    err = InvalidTransitionError(what="x", why="y", action="z")
    assert err.exit_code == 1


def test_all_error_subclasses_inherit_hpnc_error() -> None:
    subclasses = [
        ConfigError,
        ConnectivityError,
        ValidationError,
        TaskBlockedError,
        TaskInterruptedError,
        InvalidTransitionError,
    ]
    for cls in subclasses:
        err = cls(what="x", why="y", action="z")
        assert isinstance(err, HpncError), f"{cls.__name__} must inherit HpncError"
