"""ProcessLock — cross-platform file locking for dispatcher exclusivity (NFR14).

Prevents concurrent dispatcher instances from running simultaneously.
Uses msvcrt on Windows, fcntl on POSIX.
"""

from __future__ import annotations

import io
import os
import sys
from pathlib import Path
from types import TracebackType

from hpnc.infra.errors import HpncError

__all__ = ["ProcessLock"]


def _is_pid_alive(pid: int) -> bool:
    """Check if a process with the given PID is still running.

    Args:
        pid: Process ID to check.

    Returns:
        True if the process exists, False otherwise.
    """
    if sys.platform == "win32":
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.OpenProcess(0x1000, False, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            return True  # Process exists but we can't signal it


class ProcessLock:
    """Cross-platform file lock for dispatcher exclusivity.

    Can be used as a context manager for safe acquire/release.

    Args:
        lock_path: Path to the lock file.
    """

    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._file_handle: io.TextIOWrapper | None = None

    def acquire(self) -> None:
        """Acquire the lock. Creates the lock file and writes the current PID.

        If a stale lock exists (PID no longer alive), the lock is reclaimed.

        Raises:
            HpncError: If the lock is already held by a running process.
        """
        if self.lock_path.exists():
            try:
                existing_pid = int(self.lock_path.read_text().strip())
            except (ValueError, OSError):
                existing_pid = -1

            if existing_pid > 0 and _is_pid_alive(existing_pid):
                raise HpncError(
                    what="Dispatcher lock already held",
                    why=f"Process {existing_pid} holds the lock at {self.lock_path}",
                    action="Wait for the running dispatcher to finish, or remove the lock file manually",
                )
            # Stale lock — reclaim it
            try:
                self.lock_path.unlink()
            except OSError:
                pass

        self.lock_path.parent.mkdir(parents=True, exist_ok=True)

        handle = open(self.lock_path, "w")  # noqa: SIM115
        try:
            self._platform_lock(handle)
        except OSError as e:
            handle.close()
            raise HpncError(
                what="Failed to acquire dispatcher lock",
                why=str(e),
                action="Check if another dispatcher is running",
            ) from e
        handle.write(str(os.getpid()))
        handle.flush()
        self._file_handle = handle

    def _platform_lock(self, handle: io.TextIOWrapper) -> None:
        """Apply platform-specific file lock.

        Args:
            handle: Open file handle to lock.
        """
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl  # type: ignore[import-not-found,unused-ignore]

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)

    def _platform_unlock(self, handle: io.TextIOWrapper) -> None:
        """Remove platform-specific file lock.

        Args:
            handle: Open file handle to unlock.
        """
        if sys.platform == "win32":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl  # type: ignore[import-not-found,unused-ignore]

            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def release(self) -> None:
        """Release the lock and remove the lock file."""
        if self._file_handle is not None:
            try:
                self._platform_unlock(self._file_handle)
                self._file_handle.close()
            except OSError:
                pass
            self._file_handle = None

        try:
            self.lock_path.unlink()
        except OSError:
            pass

    def __enter__(self) -> ProcessLock:
        """Acquire the lock when entering context."""
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Release the lock when exiting context."""
        self.release()
