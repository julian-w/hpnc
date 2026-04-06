"""Smoke test — verifies package is importable and version exists."""

from hpnc import __version__


def test_version_exists() -> None:
    """Package version is defined and non-empty."""
    assert __version__
    assert isinstance(__version__, str)
