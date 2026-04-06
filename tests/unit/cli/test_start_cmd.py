"""Tests for hpnc start command helpers."""

import pytest

from hpnc.cli.start_cmd import _parse_delay, _wait_until


def test_parse_delay_minutes() -> None:
    assert _parse_delay("30m") == 1800.0


def test_parse_delay_hours() -> None:
    assert _parse_delay("2h") == 7200.0


def test_parse_delay_seconds() -> None:
    assert _parse_delay("90s") == 90.0


def test_parse_delay_bare_number() -> None:
    assert _parse_delay("60") == 60.0


def test_parse_delay_negative_raises() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        _parse_delay("-30m")


def test_wait_until_invalid_format_raises() -> None:
    import io

    from rich.console import Console

    console = Console(file=io.StringIO())
    with pytest.raises(ValueError, match="Invalid time format"):
        _wait_until("never", console)


def test_wait_until_invalid_hour_raises() -> None:
    import io

    from rich.console import Console

    console = Console(file=io.StringIO())
    with pytest.raises(ValueError, match="Invalid time"):
        _wait_until("25:00", console)
