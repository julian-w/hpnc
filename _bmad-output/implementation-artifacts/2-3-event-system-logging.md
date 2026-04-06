# Story 2.3: Event System & Logging

Status: done

## Story

As a developer,
I want a TaskEventListener that persists status changes to run.yaml and configurable logging,
so that every state transition is recorded and the night run is fully observable.

## Acceptance Criteria

1. `FileEventListener` in `events/file_listener.py` implements `TaskEventListener` Protocol
2. `on_status_change()` writes the new status to `run.yaml` via `Workspace.write_yaml_atomic()` (NFR2)
3. `on_progress()` appends progress detail to the run log
4. `on_complete()` writes final `RunResult` to `run.yaml` with all mandatory fields (FR50)
5. Every status transition is persisted to disk immediately — no batching (NFR2)
6. Logging setup in `infra/logging.py` uses stdlib `logging` with Rich handler for terminal output
7. `logging.FileHandler` writes to run-specific log files
8. Verbosity is configurable: minimal, normal, verbose (FR76)
9. Agent output capture supports full, truncated, or none modes (FR77)
10. Log format includes timestamps at all verbosity levels (NFR5)
11. Unit tests verify FileEventListener writes correct YAML structure
12. Unit tests verify logging configuration at each verbosity level

## Tasks / Subtasks

- [x] Task 1: Implement FileEventListener in `src/hpnc/events/file_listener.py` (AC: 1, 2, 3, 4, 5)
  - [x] Replace stub with full implementation, keeping `run_dir: Path` constructor
  - [x] Add `workspace: Workspace` constructor parameter for atomic writes
  - [x] `on_status_change(task, old, new)`: write `{"task": task, "status": new.value, "previous": old.value}` to `run.yaml` via `workspace.write_yaml_atomic()`
  - [x] `on_progress(task, phase, detail)`: log progress via Python logging (logger.info)
  - [x] `on_complete(task, result)`: write full RunResult to `run.yaml` as dict with all mandatory fields (status, executor, reviewer, branch, started, finished, files_changed, story_source)
  - [x] Every write is immediate — no batching, no buffering (NFR2)
  - [x] Update `src/hpnc/events/__init__.py` if needed

- [x] Task 2: Create logging setup in `src/hpnc/infra/logging.py` (AC: 6, 7, 8, 9, 10)
  - [x] Define `setup_logging(verbosity: str = "normal", log_file: Path | None = None, agent_output: str = "full") -> logging.Logger`
  - [x] Verbosity mapping: `"minimal"` -> WARNING, `"normal"` -> INFO, `"verbose"` -> DEBUG
  - [x] Terminal handler: use `rich.logging.RichHandler` for colored output
  - [x] File handler: `logging.FileHandler` if `log_file` is provided, plain text with timestamps
  - [x] Log format: `"%(asctime)s [%(levelname)s] %(name)s: %(message)s"` — timestamps at all levels (NFR5)
  - [x] Agent output capture mode stored as module-level config for downstream use
  - [x] Define `AgentOutputMode` Enum: FULL, TRUNCATED, NONE
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 3: Write unit tests for FileEventListener (AC: 11)
  - [x] File: `tests/unit/events/test_file_listener.py`
  - [x] `test_file_listener_on_status_change_writes_yaml` — verify run.yaml contains status
  - [x] `test_file_listener_on_status_change_immediate_persist` — verify file exists after call
  - [x] `test_file_listener_on_complete_writes_all_fields` — verify all RunResult fields in YAML
  - [x] `test_file_listener_on_complete_mandatory_fields` — verify status, executor, reviewer, branch, started, finished, files_changed, story_source
  - [x] `test_file_listener_satisfies_protocol` — isinstance check

- [x] Task 4: Write unit tests for logging setup (AC: 12)
  - [x] File: `tests/unit/infra/test_logging.py`
  - [x] `test_setup_logging_minimal_level_is_warning`
  - [x] `test_setup_logging_normal_level_is_info`
  - [x] `test_setup_logging_verbose_level_is_debug`
  - [x] `test_setup_logging_file_handler_created` — when log_file is provided
  - [x] `test_setup_logging_format_includes_timestamp` — verify asctime in format

- [x] Task 5: Verify everything passes (AC: all)
  - [x] Run `ruff check src/ tests/` — zero errors
  - [x] Run `mypy --strict src/` — zero errors
  - [x] Run `pytest -v` — all tests pass (67 existing + new)

## Dev Notes

### Critical Architecture Decisions

- **FileEventListener uses Workspace for writes**: All writes go through `Workspace.write_yaml_atomic()` for atomicity (NFR2, NFR11). FileEventListener does NOT use raw `open()`.

- **Immediate persistence**: Every `on_status_change()` call writes to disk immediately. No batching, no buffering, no in-memory accumulation. If the process crashes after a transition, the last state is on disk.

- **run.yaml is overwritten, not appended**: Each `on_status_change()` overwrites run.yaml with the current state. The history of transitions is in the log file, not run.yaml. `on_complete()` writes the final full RunResult.

- **Logging uses Rich for terminal, plain text for files**: `rich.logging.RichHandler` for colored terminal output (Rich is already a dependency). `logging.FileHandler` for run-specific log files with timestamps. No additional dependencies needed.

- **Verbosity maps to logging levels**: minimal=WARNING, normal=INFO, verbose=DEBUG. This is standard Python practice and gives predictable behavior.

### run.yaml Canonical Format (FR50)

```yaml
status: done
executor: opus
reviewer: codex
branch: night/login-validation
started: 2026-04-06T23:12:00
finished: 2026-04-06T23:36:00
files_changed:
  - src/components/LoginForm.tsx
story_source: stories/login-validation.md
```

### Import Rules

- `events/file_listener.py` may import from: `events/base.py`, `core/state_machine.py`, `infra/workspace.py`, stdlib, `logging`
- `infra/logging.py` may import from: `rich.logging`, stdlib `logging`, `pathlib`
- Neither may import from `cli/`, `agents/`, `gates/`

### Previous Story Intelligence

- **FileEventListener stub** exists with `run_dir: Path` constructor and NotImplementedError methods
- **Workspace** fully implemented in Story 2.1 with `write_yaml_atomic()`
- **RunResult** dataclass in `events/base.py` with all mandatory fields
- **TaskState** enum in `core/state_machine.py`
- **Rich** (`rich>=13`) already a project dependency
- **67 existing tests** — must not regress
- **`__init__.py` convention**: always add re-export imports alongside `__all__`

### References

- [Source: architecture.md#Dispatcher ↔ Task-Runner Communication] — FileEventListener Phase 1
- [Source: architecture.md#Logging] — stdlib logging + Rich handler + FileHandler
- [Source: architecture.md#Logging Convention] — level usage guidelines
- [Source: architecture.md#run.yaml format] — mandatory fields
- [Source: epics.md#Story 2.3] — acceptance criteria
- [Source: prd.md#Logging & Observability] — FR76-FR77

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

### Completion Notes List

- FileEventListener: on_status_change writes run.yaml immediately, on_complete writes all FR50 fields
- Logging: Rich terminal + FileHandler, verbosity minimal/normal/verbose, AgentOutputMode enum
- 10 new tests (5 listener + 5 logging), 77 total at time of completion

### Change Log

- 2026-04-06: Story 2.3 implementation complete

### File List

- src/hpnc/events/file_listener.py (replaced stub)
- src/hpnc/infra/logging.py (created)
- src/hpnc/infra/__init__.py (modified)
- tests/unit/events/__init__.py (created)
- tests/unit/events/test_file_listener.py (created)
- tests/unit/infra/test_logging.py (created)
