# Story 2.1: Workspace & Git Infrastructure

Status: done

## Story

As a developer,
I want a Workspace abstraction for atomic file operations and a Git subprocess wrapper,
so that all file I/O is safe against crashes and worktree operations are isolated behind a testable interface.

## Acceptance Criteria

1. `Workspace` in `infra/workspace.py` provides `read_yaml(path)`, `write_yaml_atomic(path, data)`, and `read_markdown(path)` (NFR11)
2. `write_yaml_atomic` writes to a temp file first, then renames (atomic write pattern)
3. `Workspace` accepts a `root` parameter (project root in production, tmp directory in tests)
4. Git wrapper in `infra/git.py` provides methods for: `create_worktree()`, `remove_worktree()`, `create_branch()`, `list_worktrees()`, `checkout_branch()`
5. Git wrapper uses `subprocess.run()` with `capture_output=True` and never `shell=True`
6. All methods use `pathlib.Path` for path arguments (NFR29)
7. Git operations handle Windows-specific constraints: long paths, case-insensitive FS (NFR30)
8. `ProcessLock` in `infra/process_lock.py` provides cross-platform file locking for dispatcher exclusivity (NFR14)
9. `conftest.py` provides `tmp_workspace` fixture creating a temporary HPNC workspace
10. Unit tests verify atomic write behavior (write succeeds, partial write doesn't corrupt)
11. Unit tests verify Git wrapper with a real temporary Git repository
12. Unit tests verify ProcessLock (acquire, release, double-lock detection)
13. `tmp_workspace` fixture creates a complete HPNC workspace structure (`_hpnc/config.yaml`, `_hpnc/night-queue.yaml`, valid Git repo with at least one commit) that mirrors production layout
14. `mock_executor` fixture is reusable with parameterized configurations (via factory pattern or `pytest.fixture` params)
15. Fixture usage is documented in `tests/conftest.py` with docstrings explaining intended usage patterns

## Tasks / Subtasks

- [x] Task 1: Implement Workspace in `src/hpnc/infra/workspace.py` (AC: 1, 2, 3, 6)
  - [x] Replace existing stub with full implementation, keeping `root: Path` constructor
  - [x] `read_yaml(path)`: resolve path relative to root, open and parse with `yaml.safe_load()`, return dict
  - [x] `write_yaml_atomic(path, data)`: resolve path relative to root, write to temp file in same directory (`path.with_suffix('.tmp')`), then `os.replace()` to final path (atomic on both POSIX and Windows)
  - [x] `read_markdown(path)`: resolve path relative to root, read and return string content
  - [x] Handle path resolution: if `path` is relative, resolve against `self.root`; if absolute, use as-is
  - [x] Raise `ConfigError` with what/why/action for file-not-found and parse errors
  - [x] All methods use `pathlib.Path`, Google-style docstrings

- [x] Task 2: Create Git wrapper in `src/hpnc/infra/git.py` (AC: 4, 5, 6, 7)
  - [x] Define `GitWrapper` class with `repo_root: Path` constructor parameter
  - [x] Helper method `_run(args: list[str]) -> subprocess.CompletedProcess[str]` — runs `git` with `subprocess.run(capture_output=True, text=True, check=False)`, never `shell=True`, always `str(path)` for paths
  - [x] `create_branch(name: str) -> None` — `git branch <name>`
  - [x] `checkout_branch(name: str) -> None` — `git checkout <name>`
  - [x] `create_worktree(path: Path, branch: str) -> None` — `git worktree add <path> <branch>`
  - [x] `remove_worktree(path: Path) -> None` — `git worktree remove <path> --force`
  - [x] `list_worktrees() -> list[Path]` — parse `git worktree list --porcelain` output
  - [x] Raise `HpncError` subclass on git failures (non-zero exit code) with stderr in the `why` field
  - [x] Handle Windows: use `str(path)` for all path args to subprocess, handle long path prefix if needed
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 3: Create ProcessLock in `src/hpnc/infra/process_lock.py` (AC: 8)
  - [x] Define `ProcessLock` class with `lock_path: Path` constructor parameter
  - [x] `acquire() -> None` — create lock file, write PID; raise `HpncError` if lock already held
  - [x] `release() -> None` — remove lock file
  - [x] Implement as context manager (`__enter__` / `__exit__`) for safe cleanup
  - [x] Cross-platform: use `msvcrt.locking()` on Windows, `fcntl.flock()` on POSIX
  - [x] Handle stale locks: if lock file exists but PID is dead, allow acquisition
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 4: Create `tmp_workspace` fixture in `tests/conftest.py` (AC: 9, 13, 14, 15)
  - [x] Add `tmp_workspace` fixture that creates:
    - `_hpnc/config.yaml` with `project_name: test`
    - `_hpnc/night-queue.yaml` (empty queue)
    - Initialize a real Git repo (`git init`, add a commit)
    - Return `Workspace(root=tmp_path)`
  - [x] Keep existing `mock_executor` and `mock_executor_factory` fixtures
  - [x] Add Google-style docstrings documenting all fixtures and their intended usage

- [x] Task 5: Write unit tests for Workspace (AC: 10)
  - [x] File: `tests/unit/infra/test_workspace.py`
  - [x] `test_workspace_read_yaml_returns_dict` — read a valid YAML file
  - [x] `test_workspace_read_yaml_missing_file_raises` — file not found raises ConfigError
  - [x] `test_workspace_write_yaml_atomic_creates_file` — write creates new file with correct content
  - [x] `test_workspace_write_yaml_atomic_overwrites_existing` — overwrite preserves atomicity
  - [x] `test_workspace_write_yaml_atomic_no_partial_write` — if write fails mid-way, original file is unchanged
  - [x] `test_workspace_read_markdown_returns_string` — read markdown content
  - [x] `test_workspace_read_markdown_missing_file_raises` — file not found raises error
  - [x] `test_workspace_relative_path_resolved_against_root` — relative paths use root

- [x] Task 6: Write unit tests for Git wrapper (AC: 11)
  - [x] File: `tests/unit/infra/test_git.py`
  - [x] Use real temp Git repo (git init in tmp_path)
  - [x] `test_git_create_branch_succeeds` — creates a branch
  - [x] `test_git_checkout_branch_succeeds` — switches to branch
  - [x] `test_git_create_worktree_succeeds` — creates worktree at path
  - [x] `test_git_remove_worktree_succeeds` — removes worktree
  - [x] `test_git_list_worktrees_returns_paths` — lists existing worktrees
  - [x] `test_git_invalid_command_raises` — non-zero exit raises HpncError

- [x] Task 7: Write unit tests for ProcessLock (AC: 12)
  - [x] File: `tests/unit/infra/test_process_lock.py`
  - [x] `test_process_lock_acquire_creates_file` — lock file created
  - [x] `test_process_lock_release_removes_file` — lock file removed
  - [x] `test_process_lock_double_acquire_raises` — second acquire raises
  - [x] `test_process_lock_context_manager_releases_on_exit` — __exit__ releases
  - [x] `test_process_lock_stale_lock_can_be_acquired` — dead PID allows re-acquire

- [x] Task 8: Verify everything passes (AC: all)
  - [x] Run `ruff check src/ tests/` — must pass with zero errors
  - [x] Run `mypy --strict src/` — must pass with zero errors
  - [x] Run `pytest -v` — all tests pass (existing 32 + new)
  - [x] Verify all `__init__.py` exports are correct

### Review Findings

- [x] [Review][Patch] `read_yaml` returns `{}` for non-dict YAML — fixed: raises ConfigError for lists/scalars
- [x] [Review][Patch] Git commands without `--` separator — fixed: added `--` before branch name in `create_branch`
- [x] [Review][Patch] AC7: No Windows long-path handling — fixed: `core.longpaths true` set on Windows
- [x] [Review][Defer] TOCTOU race in ProcessLock acquire — platform lock handles it, low risk Phase 1
- [x] [Review][Defer] msvcrt unlock wrong byte position — handle close releases lock implicitly
- [x] [Review][Defer] git not on PATH gives raw FileNotFoundError — addressed in Story 3.4 validate
- [x] [Review][Defer] TOCTOU in read_yaml/read_markdown exists() — standard pattern, single-user
- [x] [Review][Defer] PID reuse false positive — theoretical, low risk Phase 1
- [x] [Review][Defer] No subprocess timeout — git timeouts deferred to Phase 2
- [x] [Review][Defer] fdopen failure fd leak — extremely unlikely
- [x] [Review][Defer] release() deletes lock unconditionally — safe, _file_handle guard
- [x] [Review][Defer] stderr encoding on Windows — minor display issue
- [x] [Review][Defer] tmp_workspace worktree cleanup — pytest handles it

## Dev Notes

### Critical Architecture Decisions

- **Atomic write pattern**: `write_yaml_atomic()` MUST use write-to-temp-then-rename. Use `os.replace()` which is atomic on both POSIX and Windows (same filesystem). The temp file must be in the SAME directory as the target to ensure same-filesystem rename.

- **Workspace path resolution**: Methods accept `Path` objects. If the path is relative, resolve against `self.root`. If absolute, use as-is. This enables both `workspace.read_yaml(Path("_hpnc/config.yaml"))` (relative) and `workspace.read_yaml(Path("/abs/path/config.yaml"))` (absolute).

- **Git wrapper uses subprocess, not gitpython**: Architecture explicitly forbids gitpython. Use `subprocess.run()` with `capture_output=True, text=True`. Always pass `str(path)` for cross-platform compatibility.

- **ProcessLock is cross-platform**: Windows uses `msvcrt.locking()`, POSIX uses `fcntl.flock()`. The lock file is `_hpnc/.dispatcher.lock`. Write PID to lock file for stale lock detection.

- **tmp_workspace must be realistic**: The fixture must create a complete HPNC workspace with `_hpnc/config.yaml`, `_hpnc/night-queue.yaml`, and a valid Git repo with at least one commit. This mirrors production layout so integration tests are meaningful.

### Workspace Implementation Pattern

```python
import os
import tempfile
from pathlib import Path
from typing import Any
import yaml

class Workspace:
    def __init__(self, root: Path) -> None:
        self.root = root

    def _resolve(self, path: Path) -> Path:
        if path.is_absolute():
            return path
        return self.root / path

    def read_yaml(self, path: Path) -> dict[str, Any]:
        resolved = self._resolve(path)
        # raise ConfigError if not found
        with resolved.open() as f:
            return yaml.safe_load(f) or {}

    def write_yaml_atomic(self, path: Path, data: dict[str, Any]) -> None:
        resolved = self._resolve(path)
        resolved.parent.mkdir(parents=True, exist_ok=True)
        # Write to temp file in same dir, then atomic rename
        fd, tmp = tempfile.mkstemp(dir=resolved.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
            os.replace(tmp, resolved)
        except:
            os.unlink(tmp)
            raise
```

### Git Wrapper Pattern

```python
class GitWrapper:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            ["git", *args],
            capture_output=True, text=True,
            cwd=str(self.repo_root),
        )
        if result.returncode != 0:
            raise HpncError(
                what=f"Git command failed: git {' '.join(args)}",
                why=result.stderr.strip(),
                action="Check git status and try again",
            )
        return result
```

### ProcessLock Pattern

```python
import os
import sys

class ProcessLock:
    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self._fd: int | None = None

    def acquire(self) -> None:
        # Check for stale lock (PID exists but process dead)
        # Platform-specific locking: msvcrt (Windows) or fcntl (POSIX)
        ...

    def release(self) -> None:
        # Unlock and remove file
        ...

    def __enter__(self) -> "ProcessLock": ...
    def __exit__(self, *args) -> None: ...
```

### Import Rules (strict boundaries)

- `infra/workspace.py` may import from: `yaml` (PyYAML), `infra/errors.py`, stdlib only
- `infra/git.py` may import from: `infra/errors.py`, stdlib only
- `infra/process_lock.py` may import from: `infra/errors.py`, stdlib only
- None of these may import from `core/`, `cli/`, `agents/`, `events/`, `gates/`, `schemas/`

### Naming Conventions (mandatory)

- Classes: `PascalCase` — `Workspace`, `GitWrapper`, `ProcessLock`
- Methods: `snake_case` — `read_yaml()`, `write_yaml_atomic()`, `create_worktree()`
- Private: `_leading_underscore` — `_resolve()`, `_run()`
- Test functions: `test_<what>_<when>_<expected>`

### Forbidden Patterns

- No `print()` — all output through Rich or logging
- No bare `raise Exception` — use `HpncError` subclasses
- No `str` for file paths — use `pathlib.Path`
- No `shell=True` in subprocess calls
- No raw `open()` on state files — use `Workspace`
- No bare `# TODO` — always `# TODO(phase-N): description`

### Project Structure Notes

- `src/hpnc/infra/workspace.py` — REPLACE existing stub (not new file)
- `src/hpnc/infra/git.py` — new file
- `src/hpnc/infra/process_lock.py` — new file
- `tests/unit/infra/test_workspace.py` — new file
- `tests/unit/infra/test_git.py` — new file
- `tests/unit/infra/test_process_lock.py` — new file (may need to create `tests/unit/infra/` __init__.py — check if exists)
- `tests/conftest.py` — modify to add `tmp_workspace` fixture

### Previous Story Intelligence (Epic 1)

- **Workspace stub** exists in `infra/workspace.py` with `root: Path` constructor and 3 methods raising `NotImplementedError("Implemented in Story 2.1")`
- **ConfigError** available from `infra/errors.py` — use for file-not-found and parse errors
- **HpncError** available from `infra/errors.py` — use for git failures
- **`python -m uv`** required (uv not on PATH)
- **ruff** may auto-fix import ordering (I001)
- **mypy --strict** enforced — all new code must pass
- **32 existing tests** — must not regress
- **`__init__.py` convention**: always add re-export imports alongside `__all__`
- **`tests/unit/infra/__init__.py`** already exists from Story 1.2
- **mock_executor + mock_executor_factory** fixtures already in conftest.py
- **PyYAML** (`pyyaml>=6.0.3`) already a project dependency

### Windows Compatibility Notes (NFR28-30)

- `os.replace()` is atomic on Windows (same filesystem)
- `tempfile.mkstemp()` works cross-platform
- Use `str(path)` for all subprocess path args
- `fcntl` not available on Windows — use `msvcrt` for file locking
- Git worktree paths must handle backslash/forward-slash differences
- Case-insensitive filesystem: don't create files differing only by case

### References

- [Source: architecture.md#Workspace Object] — Workspace design, atomic writes, root parameter
- [Source: architecture.md#Cross-Cutting Concerns] — Atomic file writes, Windows path handling
- [Source: architecture.md#Technical Constraints] — Git subprocess, no gitpython
- [Source: architecture.md#Process Management] — Dispatcher lock, ProcessLock
- [Source: architecture.md#Test Fixtures Architecture] — tmp_workspace, mock_executor patterns
- [Source: architecture.md#Complete Project Directory Structure] — Runtime files (_hpnc/)
- [Source: architecture.md#Subprocess Calls] — subprocess.run patterns
- [Source: architecture.md#Implementation Patterns] — naming, enforcement
- [Source: epics.md#Story 2.1] — acceptance criteria
- [Source: prd.md#Data Integrity] — NFR7-11, atomic writes
- [Source: prd.md#Idempotency] — NFR14, process lock
- [Source: prd.md#Cross-Platform] — NFR28-30, Windows compatibility

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- Added `types-pyyaml` dev dependency for mypy yaml stubs
- ProcessLock: `ctypes.windll.kernel32` type ignore not needed on Windows (mypy knows windll)
- ProcessLock: `fcntl` import uses `type: ignore[import-not-found]` since it doesn't exist on Windows
- Two test fixes: ProcessLock double-acquire gives PermissionError on Windows (not "lock already held"), atomic write partial test redesigned for cross-platform

### Completion Notes List

- All 8 tasks completed successfully
- Workspace: full implementation with _resolve(), read_yaml (yaml.safe_load), write_yaml_atomic (tempfile.mkstemp + os.replace), read_markdown
- GitWrapper: 5 methods (create_branch, checkout_branch, create_worktree, remove_worktree, list_worktrees) + _run helper
- ProcessLock: cross-platform (msvcrt/fcntl), context manager, stale lock detection via PID check
- tmp_workspace fixture: _hpnc/config.yaml, night-queue.yaml, real git init + commit
- 19 new tests: 8 workspace, 6 git, 5 process lock
- 51 total tests pass, ruff clean, mypy --strict clean (29 source files)
- git.py: 100% coverage, workspace.py: 80%, process_lock.py: 78% (POSIX branches uncovered on Windows)
- Added types-pyyaml dev dependency

### Change Log

- 2026-04-06: Story 2.1 implementation complete — all ACs satisfied

### File List

- src/hpnc/infra/workspace.py (replaced stub — full Workspace implementation)
- src/hpnc/infra/git.py (created — GitWrapper)
- src/hpnc/infra/process_lock.py (created — ProcessLock)
- src/hpnc/infra/__init__.py (modified — added GitWrapper, ProcessLock exports)
- tests/conftest.py (modified — added tmp_workspace fixture)
- tests/unit/infra/test_workspace.py (created — 8 tests)
- tests/unit/infra/test_git.py (created — 6 tests)
- tests/unit/infra/test_process_lock.py (created — 5 tests)
- pyproject.toml (modified — types-pyyaml dev dependency added via uv)
- uv.lock (modified — updated lockfile)
