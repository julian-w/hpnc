# Story 1.2: Core Interfaces, State Machine & Error Hierarchy

Status: done

## Story

As a developer,
I want all Protocol interfaces, the state machine, the frontmatter schema, and the error hierarchy defined,
so that every subsequent module can be developed against stable interfaces with a tested core.

## Acceptance Criteria

1. `AgentExecutor` Protocol exists in `agents/base.py` with 3 methods: `start()`, `stream_output()`, `get_exit_status()` (FR75)
2. `TaskEventListener` Protocol exists in `events/base.py` with methods: `on_status_change()`, `on_progress()`, `on_complete()`
3. `TaskState` Enum in `core/state_machine.py` contains all Phase 1 states (QUEUED, SETUP_WORKTREE, IMPLEMENTATION, REVIEW, GATES, DONE, FAILED, BLOCKED) and Phase 2 labels (FIX_ATTEMPT, PAUSED, AWAITING_REVIEW, PROPOSAL, MERGED, INTERRUPTED)
4. Phase 1 transition table is implemented as a pure function (no I/O, no dependencies)
5. Invalid state transitions raise an appropriate error
6. `HpncError` base class exists in `infra/errors.py` with `what`, `why`, `action` fields (NFR24)
7. Subclasses exist: `ConfigError`, `ConnectivityError`, `ValidationError`, `TaskBlockedError`, `TaskInterruptedError` with mapped exit codes (0-5)
8. Frontmatter schema is defined in `schemas/frontmatter.py` with all night-ready fields (night_ready, executor, reviewer, risk, tests_required, touches, blocking_questions, gates_required) (FR16)
9. `ConfigLoader` stub exists in `infra/config.py` with `find_root()` method signature (FR7)
10. `Workspace` stub exists in `infra/workspace.py` with method signatures for `read_yaml()`, `write_yaml_atomic()`, `read_markdown()`
11. Unit tests exist for all state machine transitions (`test_state_machine_queued_to_setup_worktree_succeeds`, invalid transition test, all Phase 1 paths)
12. Unit tests exist for HpncError hierarchy (correct exit codes, format)
13. All paths use `pathlib.Path`, never `str` (NFR29)

## Tasks / Subtasks

- [x] Task 1: Create HpncError hierarchy in `src/hpnc/infra/errors.py` (AC: 6, 7)
  - [x] Define `HpncError` base with `what`, `why`, `action` fields as `__init__` params and instance attributes
  - [x] Define `exit_code` property on base class (default 1), overridden per subclass
  - [x] Create subclasses: `ConfigError` (exit code 4), `ConnectivityError` (exit code 5), `ValidationError` (exit code 1), `TaskBlockedError` (exit code 2), `TaskInterruptedError` (exit code 3)
  - [x] Implement `__str__` returning formatted message: `"{what}: {why}\n  Action: {action}"`
  - [x] Add `InvalidTransitionError(HpncError)` for state machine invalid transitions (AC: 5)
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 2: Create TaskState Enum and state machine in `src/hpnc/core/state_machine.py` (AC: 3, 4, 5)
  - [x] Define `TaskState` Enum with all 14 states: 8 Phase 1 (QUEUED, SETUP_WORKTREE, IMPLEMENTATION, REVIEW, GATES, DONE, FAILED, BLOCKED) + 6 Phase 2 (FIX_ATTEMPT, PAUSED, AWAITING_REVIEW, PROPOSAL, MERGED, INTERRUPTED)
  - [x] Enum values are lowercase snake_case strings matching architecture: `"queued"`, `"setup_worktree"`, etc.
  - [x] Define `TRANSITIONS: dict[TaskState, list[TaskState]]` — Phase 1 only (see architecture below)
  - [x] Define `TERMINAL_STATES: frozenset[TaskState]` = `{DONE, FAILED, BLOCKED}`
  - [x] Implement `transition(current: TaskState, target: TaskState) -> TaskState` as a module-level pure function
  - [x] `transition()` raises `InvalidTransitionError` if target not in `TRANSITIONS[current]`
  - [x] `transition()` raises `InvalidTransitionError` if current is a terminal state
  - [x] Update `src/hpnc/core/__init__.py` exports

- [x] Task 3: Create AgentExecutor Protocol in `src/hpnc/agents/base.py` (AC: 1, 13)
  - [x] Define supporting types first: `ExitStatus` Enum (SUCCESS, FAILURE, TIMEOUT) in same file
  - [x] Define `AgentExecutor` as `typing.Protocol` with runtime_checkable decorator
  - [x] Method: `def start(self, story: Path, config: "Config", instructions: Path) -> subprocess.Popen[str]`
  - [x] Method: `def stream_output(self, process: subprocess.Popen[str]) -> Iterator[str]`
  - [x] Method: `def get_exit_status(self, process: subprocess.Popen[str]) -> ExitStatus`
  - [x] Use forward reference `"Config"` for config parameter (avoid circular import with infra)
  - [x] All path params typed as `pathlib.Path`
  - [x] Update `src/hpnc/agents/__init__.py` exports

- [x] Task 4: Create TaskEventListener Protocol in `src/hpnc/events/base.py` (AC: 2)
  - [x] Define `RunResult` dataclass in same file: `status: TaskState`, `executor: str`, `reviewer: str`, `branch: str`, `started: str`, `finished: str`, `files_changed: list[str]`, `story_source: str`
  - [x] Define `TaskEventListener` as `typing.Protocol` with runtime_checkable
  - [x] Method: `def on_status_change(self, task: str, old: TaskState, new: TaskState) -> None`
  - [x] Method: `def on_progress(self, task: str, phase: str, detail: str) -> None`
  - [x] Method: `def on_complete(self, task: str, result: RunResult) -> None`
  - [x] Update `src/hpnc/events/__init__.py` exports

- [x] Task 5: Create frontmatter schema in `src/hpnc/schemas/frontmatter.py` (AC: 8)
  - [x] Define `FrontmatterSchema` as a dataclass with all night-ready fields:
    - `night_ready: bool`
    - `executor: str` (e.g., "opus", "codex")
    - `reviewer: str` (e.g., "codex", "opus")
    - `risk: str` (e.g., "low", "medium", "high")
    - `tests_required: bool`
    - `touches: list[str]` (abstract resource names)
    - `blocking_questions: list[str]` (must be empty for night-ready)
    - `gates_required: list[str]` (e.g., ["build", "tests", "lint"])
  - [x] Define `KNOWN_GATES: frozenset[str]` = `{"build", "tests", "lint"}`
  - [x] Define `KNOWN_EXECUTORS: frozenset[str]` = `{"opus", "codex", "mock"}`
  - [x] Define `MANDATORY_FIELDS: frozenset[str]` listing fields required for night_ready validation
  - [x] Update `src/hpnc/schemas/__init__.py` exports

- [x] Task 6: Create ConfigLoader stub in `src/hpnc/infra/config.py` (AC: 9, 13)
  - [x] Define `Config` dataclass with fields matching `_hpnc/config.yaml` schema:
    - `project_name: str`
    - `project_root: Path`
    - `merge_target: str` (default: "main")
    - `log_verbosity: str` (default: "normal")
    - `agent_output: str` (default: "full")
  - [x] Define `ConfigLoader` class with stub methods:
    - `find_root(start: Path | None = None) -> Path` — searches upward for `_hpnc/config.yaml`, raises `ConfigError` if not found
    - `load(root: Path) -> Config` — parses config.yaml, returns Config
  - [x] Method bodies: `raise NotImplementedError("Implemented in Story 2.1")` — NOT `pass` or `...`
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 7: Create Workspace stub in `src/hpnc/infra/workspace.py` (AC: 10, 13)
  - [x] Define `Workspace` class with `root: Path` constructor parameter
  - [x] Stub methods:
    - `read_yaml(self, path: Path) -> dict[str, Any]`
    - `write_yaml_atomic(self, path: Path, data: dict[str, Any]) -> None`
    - `read_markdown(self, path: Path) -> str`
  - [x] Method bodies: `raise NotImplementedError("Implemented in Story 2.1")`
  - [x] Update `src/hpnc/infra/__init__.py` exports

- [x] Task 8: Write unit tests for state machine (AC: 11)
  - [x] File: `tests/unit/core/test_state_machine.py`
  - [x] `test_state_machine_queued_to_setup_worktree_succeeds` — verifies QUEUED -> SETUP_WORKTREE
  - [x] `test_state_machine_setup_worktree_to_implementation_succeeds`
  - [x] `test_state_machine_setup_worktree_to_failed_succeeds`
  - [x] `test_state_machine_implementation_to_review_succeeds`
  - [x] `test_state_machine_implementation_to_blocked_succeeds`
  - [x] `test_state_machine_review_to_gates_succeeds`
  - [x] `test_state_machine_review_to_blocked_succeeds`
  - [x] `test_state_machine_gates_to_done_succeeds`
  - [x] `test_state_machine_gates_to_failed_succeeds`
  - [x] `test_state_machine_invalid_transition_raises` — e.g., QUEUED -> DONE
  - [x] `test_state_machine_terminal_state_transition_raises` — DONE, FAILED, BLOCKED cannot transition
  - [x] `test_task_state_all_phase1_states_exist` — verify all 8 Phase 1 states
  - [x] `test_task_state_all_phase2_states_exist` — verify all 6 Phase 2 states
  - [x] `test_task_state_values_are_lowercase_strings` — verify enum values match architecture

- [x] Task 9: Write unit tests for error hierarchy (AC: 12)
  - [x] File: `tests/unit/infra/test_errors.py`
  - [x] `test_hpnc_error_stores_what_why_action` — verify all 3 fields accessible
  - [x] `test_hpnc_error_str_format` — verify __str__ includes all 3 fields
  - [x] `test_config_error_exit_code_is_4`
  - [x] `test_connectivity_error_exit_code_is_5`
  - [x] `test_validation_error_exit_code_is_1`
  - [x] `test_task_blocked_error_exit_code_is_2`
  - [x] `test_task_interrupted_error_exit_code_is_3`
  - [x] `test_invalid_transition_error_exit_code` — verify it has an appropriate exit code
  - [x] `test_all_error_subclasses_inherit_hpnc_error` — isinstance check for all subclasses

- [x] Task 10: Verify tooling passes (AC: all)
  - [x] Run `ruff check src/ tests/` — must pass with zero errors
  - [x] Run `mypy --strict src/` — must pass with zero errors
  - [x] Run `pytest` — all tests pass
  - [x] Verify all `__init__.py` exports are correct and consistent

### Review Findings

- [x] [Review][Patch] `__init__.py` files declare `__all__` but never import the symbols — fixed: added re-exports [src/hpnc/infra/__init__.py, core/__init__.py, agents/__init__.py, events/__init__.py, schemas/__init__.py]
- [x] [Review][Defer] Phase 2 states have no transitions — `transition()` error message doesn't distinguish "not yet wired" from "terminal" — deferred, Phase 2 concern
- [x] [Review][Defer] `TRANSITIONS` is mutable module-level dict — runtime patching could corrupt state machine — deferred, low risk in Phase 1
- [x] [Review][Defer] `HpncError` breaks `pickle` round-trip — deferred, not relevant until Phase 3+ parallelization

## Dev Notes

### Critical Architecture Decisions

- **State Machine is PURE LOGIC**: `core/state_machine.py` must have zero I/O, zero dependencies on other HPNC modules except `infra/errors.py` for `InvalidTransitionError`. It receives current state + target state, returns new state or raises. This is the most testable module in the project.

- **Protocol over ABC**: Use `typing.Protocol` for all interfaces (`AgentExecutor`, `TaskEventListener`). No inheritance required — any class implementing the methods satisfies the Protocol. Add `@runtime_checkable` to enable `isinstance()` checks.

- **Error hierarchy NFR24**: Every `HpncError` must carry `what`, `why`, `action` as named fields. The CLI layer (not this story) will catch these and format with Rich. The `__str__` method should render all three fields for debugging/logging.

- **Stubs raise NotImplementedError**: `ConfigLoader` and `Workspace` stubs must raise `NotImplementedError` with a message pointing to the implementing story, NOT use `pass` or `...`. This prevents silent failures if someone accidentally calls an unimplemented method.

- **Config forward reference**: `AgentExecutor.start()` takes a `Config` parameter. Use string forward reference `"Config"` or `TYPE_CHECKING` import to avoid circular dependency between `agents/base.py` and `infra/config.py`.

### Phase 1 Transition Table (from architecture)

```python
TRANSITIONS: dict[TaskState, list[TaskState]] = {
    TaskState.QUEUED: [TaskState.SETUP_WORKTREE],
    TaskState.SETUP_WORKTREE: [TaskState.IMPLEMENTATION, TaskState.FAILED],
    TaskState.IMPLEMENTATION: [TaskState.REVIEW, TaskState.BLOCKED],
    TaskState.REVIEW: [TaskState.GATES, TaskState.BLOCKED],
    TaskState.GATES: [TaskState.DONE, TaskState.FAILED],
}
```

Phase 2 states are defined in the Enum but have NO transitions yet. They are labels only.

### Error Hierarchy Exit Codes (from architecture)

| Error Class | Exit Code | When |
|---|---|---|
| (success) | 0 | No error |
| `ValidationError` | 1 | Frontmatter/pre-flight validation failure |
| `TaskBlockedError` | 2 | Agent cannot proceed, needs human input |
| `TaskInterruptedError` | 3 | Process terminated unexpectedly |
| `ConfigError` | 4 | Config file missing, invalid, or unreadable |
| `ConnectivityError` | 5 | Agent CLI not reachable |

`InvalidTransitionError` is an internal programming error (exit code 1 or inherit from base).

### AgentExecutor Protocol Signature (from architecture)

```python
class AgentExecutor(Protocol):
    def start(self, story: Path, config: Config, instructions: Path) -> Popen[str]: ...
    def stream_output(self, process: Popen[str]) -> Iterator[str]: ...
    def get_exit_status(self, process: Popen[str]) -> ExitStatus: ...
```

`Popen[str]` because agents are subprocess-based. `ExitStatus` is a new Enum (SUCCESS, FAILURE, TIMEOUT) defined in the same file.

### TaskEventListener Protocol Signature (from architecture)

```python
class TaskEventListener(Protocol):
    def on_status_change(self, task: str, old: TaskState, new: TaskState) -> None: ...
    def on_progress(self, task: str, phase: str, detail: str) -> None: ...
    def on_complete(self, task: str, result: RunResult) -> None: ...
```

`RunResult` is a dataclass mirroring the `run.yaml` fields from architecture.

### Frontmatter Schema Fields (from architecture + PRD)

Night-ready fields defined in FR13, FR16, FR19-FR22:
- `night_ready: bool` — master switch
- `executor: str` — which agent implements (opus, codex)
- `reviewer: str` — which agent reviews (codex, opus)
- `risk: str` — low/medium/high
- `tests_required: bool` — must be defined (FR22)
- `touches: list[str]` — abstract resources this task affects
- `blocking_questions: list[str]` — must be empty for night-ready (FR21)
- `gates_required: list[str]` — which quality gates to run

Phase 2 fields (define in schema but don't validate yet): `depends_on`, `release_policy`, `merge_policy`, `priority`.

### Naming Conventions (mandatory)

- Enum members: `UPPER_SNAKE` — `TaskState.QUEUED`, `ExitStatus.SUCCESS`
- Enum values: lowercase strings — `"queued"`, `"success"`
- Classes: `PascalCase` — `HpncError`, `ConfigLoader`, `Workspace`
- Functions: `snake_case` — `transition()`, `find_root()`
- Constants: `UPPER_SNAKE` — `TRANSITIONS`, `TERMINAL_STATES`, `KNOWN_GATES`
- Files: `snake_case` — `state_machine.py`, `errors.py`
- Test functions: `test_<what>_<when>_<expected>`

### Forbidden Patterns

- No `print()` — all output through Rich or logging
- No bare `raise Exception` — use `HpncError` subclasses
- No `str` for file paths — use `pathlib.Path`
- No magic strings — use Enums and constants
- No bare `# TODO` — always `# TODO(phase-N): description`

### Import Rules (strict boundaries)

- `core/state_machine.py` may import from: `infra/errors.py` only (for `InvalidTransitionError`)
- `agents/base.py` may import from: stdlib only (`typing`, `pathlib`, `subprocess`), forward-ref `Config`
- `events/base.py` may import from: `core/state_machine.py` (for `TaskState`)
- `schemas/frontmatter.py` may import from: stdlib only (`dataclasses`)
- `infra/errors.py` may import from: stdlib only
- `infra/config.py` may import from: `infra/errors.py` only
- `infra/workspace.py` may import from: stdlib only

### Project Structure Notes

- All files created in Story 1.1 exist as empty stubs — this story fills them with real content
- The `__init__.py` files currently have `__all__: list[str] = []` — update with actual exports
- Test directories `tests/unit/core/` and `tests/unit/infra/` may need to be created (check if they exist)
- `tests/unit/agents/` and `tests/unit/schemas/` directories may also be needed for future stories

### Previous Story Intelligence (Story 1.1)

- **uv 0.11.3** with Python 3.12.13, all deps installed
- **Typer 0.24.1** — uses `typer.echo()` for CLI stubs (will be replaced with Rich later)
- **Dependency groups** used instead of `project.optional-dependencies` (uv convention)
- **mypy --strict** already enforced — all new code must pass strict type checking
- **ruff** configured with `["E", "F", "W", "I", "UP", "B"]` rules
- **Smoke test** exists at `tests/unit/test_smoke.py` — verify it still passes after changes
- CLI stubs use `typer.echo("Not yet implemented")` — do NOT modify CLI files in this story

### References

- [Source: architecture.md#State Machine] — TaskState enum, transition table
- [Source: architecture.md#Error Handling] — HpncError hierarchy with exit codes
- [Source: architecture.md#Interfaces — Protocol] — AgentExecutor Protocol signature
- [Source: architecture.md#Dispatcher ↔ Task-Runner Communication] — TaskEventListener Protocol
- [Source: architecture.md#Project Module Structure] — file locations for all modules
- [Source: architecture.md#Architectural Boundaries] — strict import rules
- [Source: architecture.md#Walking Skeleton] — what interfaces need to be defined
- [Source: architecture.md#Gate Extensibility] — gates_required field in frontmatter
- [Source: architecture.md#Naming Patterns] — all naming conventions
- [Source: architecture.md#Code Conventions] — Protocol, docstrings, types
- [Source: architecture.md#Test Fixtures Architecture] — fixture patterns
- [Source: epics.md#Story 1.2] — acceptance criteria and BDD format
- [Source: prd.md#Task Lifecycle & State Management] — FR35-FR52, state machine requirements
- [Source: prd.md#Agent Orchestration] — FR69-FR75, AgentExecutor requirements
- [Source: prd.md#Error Messages] — NFR24, what/why/action format

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- `python -m uv` required (uv not on PATH in bash shell)
- ruff auto-fixed import ordering in test_state_machine.py (I001)

### Completion Notes List

- All 10 tasks completed successfully
- HpncError hierarchy: base + 6 subclasses with what/why/action fields and mapped exit codes (0-5)
- TaskState Enum: 14 states (8 Phase 1 + 6 Phase 2 labels), pure transition function
- AgentExecutor Protocol: 3 methods (start, stream_output, get_exit_status) + ExitStatus Enum
- TaskEventListener Protocol: 3 methods (on_status_change, on_progress, on_complete) + RunResult dataclass
- FrontmatterSchema: 8 fields + KNOWN_GATES, KNOWN_EXECUTORS, MANDATORY_FIELDS constants
- ConfigLoader stub: Config dataclass + find_root/load methods raising NotImplementedError
- Workspace stub: 3 methods raising NotImplementedError
- 15 state machine tests (9 valid transitions, 2 invalid, 4 enum completeness)
- 9 error hierarchy tests (fields, format, exit codes, inheritance)
- All 25 tests pass, ruff clean, mypy --strict clean (25 source files)
- state_machine.py: 100% coverage, errors.py: 100% coverage (except unused __str__ branch)

### Change Log

- 2026-04-06: Story 1.2 implementation complete — all ACs satisfied

### File List

- src/hpnc/infra/errors.py (created — HpncError hierarchy)
- src/hpnc/core/state_machine.py (created — TaskState enum, transitions, transition function)
- src/hpnc/agents/base.py (created — ExitStatus enum, AgentExecutor Protocol)
- src/hpnc/events/base.py (created — RunResult dataclass, TaskEventListener Protocol)
- src/hpnc/schemas/frontmatter.py (created — FrontmatterSchema, constants)
- src/hpnc/infra/config.py (created — Config dataclass, ConfigLoader stub)
- src/hpnc/infra/workspace.py (created — Workspace stub)
- src/hpnc/infra/__init__.py (modified — updated __all__ exports)
- src/hpnc/core/__init__.py (modified — updated __all__ exports)
- src/hpnc/agents/__init__.py (modified — updated __all__ exports)
- src/hpnc/events/__init__.py (modified — updated __all__ exports)
- src/hpnc/schemas/__init__.py (modified — updated __all__ exports)
- tests/unit/core/__init__.py (created)
- tests/unit/core/test_state_machine.py (created — 15 tests)
- tests/unit/infra/__init__.py (created)
- tests/unit/infra/test_errors.py (created — 9 tests)
