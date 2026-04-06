"""Tests for hpnc start command helpers."""

from hpnc.cli.start_cmd import _parse_delay


def test_parse_delay_minutes() -> None:
    assert _parse_delay("30m") == 1800.0


def test_parse_delay_hours() -> None:
    assert _parse_delay("2h") == 7200.0


def test_parse_delay_seconds() -> None:
    assert _parse_delay("90s") == 90.0


def test_parse_delay_bare_number() -> None:
    assert _parse_delay("60") == 60.0
