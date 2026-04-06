"""Tests for logging setup."""

import logging
from pathlib import Path

from hpnc.infra.logging import setup_logging


def test_setup_logging_minimal_level_is_warning() -> None:
    logger = setup_logging(verbosity="minimal")
    assert logger.level == logging.WARNING


def test_setup_logging_normal_level_is_info() -> None:
    logger = setup_logging(verbosity="normal")
    assert logger.level == logging.INFO


def test_setup_logging_verbose_level_is_debug() -> None:
    logger = setup_logging(verbosity="verbose")
    assert logger.level == logging.DEBUG


def test_setup_logging_file_handler_created(tmp_path: Path) -> None:
    log_file = tmp_path / "test.log"
    logger = setup_logging(verbosity="normal", log_file=log_file)

    # Should have at least 2 handlers: Rich + File
    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename == str(log_file)


def test_setup_logging_format_includes_timestamp(tmp_path: Path) -> None:
    log_file = tmp_path / "format.log"
    logger = setup_logging(verbosity="normal", log_file=log_file)

    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    formatter = file_handlers[0].formatter
    assert formatter is not None
    assert "asctime" in formatter._fmt  # type: ignore[union-attr]
