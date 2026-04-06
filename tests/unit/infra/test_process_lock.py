"""Tests for ProcessLock cross-platform file locking."""

from pathlib import Path

import pytest

from hpnc.infra.errors import HpncError
from hpnc.infra.process_lock import ProcessLock


def test_process_lock_acquire_creates_file(tmp_path: Path) -> None:
    lock_path = tmp_path / ".dispatcher.lock"
    lock = ProcessLock(lock_path)
    lock.acquire()
    assert lock_path.exists()
    lock.release()


def test_process_lock_release_removes_file(tmp_path: Path) -> None:
    lock_path = tmp_path / ".dispatcher.lock"
    lock = ProcessLock(lock_path)
    lock.acquire()
    lock.release()
    assert not lock_path.exists()


def test_process_lock_double_acquire_raises(tmp_path: Path) -> None:
    lock_path = tmp_path / ".dispatcher.lock"
    lock1 = ProcessLock(lock_path)
    lock1.acquire()
    lock2 = ProcessLock(lock_path)
    with pytest.raises(HpncError):
        lock2.acquire()
    lock1.release()


def test_process_lock_context_manager_releases_on_exit(tmp_path: Path) -> None:
    lock_path = tmp_path / ".dispatcher.lock"
    with ProcessLock(lock_path):
        assert lock_path.exists()
    assert not lock_path.exists()


def test_process_lock_stale_lock_can_be_acquired(tmp_path: Path) -> None:
    lock_path = tmp_path / ".dispatcher.lock"
    # Simulate stale lock with a dead PID
    lock_path.write_text("999999999")  # PID that almost certainly doesn't exist
    lock = ProcessLock(lock_path)
    lock.acquire()  # Should succeed — stale lock reclaimed
    assert lock_path.exists()
    lock.release()
