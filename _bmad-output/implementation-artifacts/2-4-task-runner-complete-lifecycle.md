# Story 2.4: Task Runner — Complete Lifecycle

Status: done

## Story

As a developer,
I want a Task Runner that processes a single task through the complete state machine lifecycle,
so that a task can autonomously move from queued to done/failed/blocked using mock agents.

## Acceptance Criteria

1. Task Runner receives dependencies via constructor injection: `executor`, `reviewer` (AgentExecutor), `gates` (GateRunner), `listener` (TaskEventListener), `workspace` (Workspace), `config` (Config)
2. Task Runner creates a named branch `night/<task-name>` and a Git worktree for the task (FR35)
3. Task Runner transitions through states: QUEUED -> SETUP_WORKTREE -> IMPLEMENTATION -> REVIEW -> GATES -> terminal (FR36)
4. During IMPLEMENTATION, Task Runner invokes the executor AgentExecutor with story, config, and instructions (FR37, FR69)
5. Agent output is streamed/buffered via AgentExecutor (FR70)
6. Agent exit status is captured (FR71)
7. During REVIEW, Task Runner invokes a different AgentExecutor instance for review (FR38)
8. If all gates pass, task transitions to DONE (FR39)
9. If any gate fails, task transitions to FAILED with gate failure details (FR40)
10. If the agent signals it cannot proceed, task transitions to BLOCKED with reason (FR41)
11. Worktree is cleaned up after task completion regardless of terminal status (FR49)
12. `run.yaml` is written with mandatory fields: status, executor, reviewer, branch, started, finished, files_changed, story_source (FR50)
13. Every state transition fires the TaskEventListener (NFR2)
14. Agent crashes are handled gracefully without orphaned worktrees (NFR6)
15. Files outside the worktree are never modified (NFR9)
16. Integration tests verify complete lifecycle: queued -> done (with mock success)
17. Integration tests verify complete lifecycle: queued -> failed (with mock gate failure)
18. Integration tests verify complete lifecycle: queued -> blocked (with mock block signal)
19. Task Runner is independently executable via `python -m hpnc.core.task_runner`

## Tasks / Subtasks

- [x] Task 1: Implement TaskRunner in `src/hpnc/core/task_runner.py` (AC: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
  - [x] Constructor: `executor: AgentExecutor`, `reviewer: AgentExecutor`, `gates: GateRunner`, `listener: TaskEventListener`, `workspace: Workspace`, `config: Config`, `git: GitWrapper`
  - [x] `run(task_name: str, story: Path, instructions: Path, worktree_base: Path) -> RunResult`
  - [x] State QUEUED -> SETUP_WORKTREE: create branch `night/<task_name>`, create worktree via GitWrapper
  - [x] State SETUP_WORKTREE -> IMPLEMENTATION: invoke `executor.start(story, config, instructions)`, stream output, capture exit status
  - [x] If executor returns FAILURE -> transition to BLOCKED (agent can't proceed)
  - [x] State IMPLEMENTATION -> REVIEW: invoke `reviewer.start(story, config, instructions)`, stream output, capture exit status
  - [x] If reviewer returns FAILURE -> transition to BLOCKED
  - [x] State REVIEW -> GATES: run `gates.run_all(worktree_path)`, check results
  - [x] If gates passed -> transition to DONE
  - [x] If gates failed -> transition to FAILED
  - [x] Fire `listener.on_status_change()` at every transition
  - [x] Fire `listener.on_complete()` at terminal state with full RunResult
  - [x] Record `started` timestamp at SETUP_WORKTREE, `finished` at terminal
  - [x] Wrap entire lifecycle in try/finally to ensure worktree cleanup (FR49, NFR6)
  - [x] On exception: transition to FAILED, log error, clean up worktree

- [x] Task 2: Update `core/__main__.py` for independent execution (AC: 19)
  - [x] Parse task-spec.yaml from command line argument
  - [x] Construct dependencies from spec (Config, Workspace, GitWrapper, MockAgentExecutor, GateRunner, FileEventListener)
  - [x] Call `TaskRunner.run()` and exit with appropriate code

- [x] Task 3: Update `core/__init__.py` exports
  - [x] Add TaskRunner to exports

- [x] Task 4: Write integration tests for complete lifecycle (AC: 16, 17, 18)
  - [x] File: `tests/integration/test_task_lifecycle.py`
  - [x] Use `tmp_workspace` fixture + `mock_executor_factory`
  - [x] `test_task_lifecycle_queued_to_done` — mock success for executor, reviewer, and gates
  - [x] `test_task_lifecycle_queued_to_failed` — mock success for executor/reviewer, mock gate failure
  - [x] `test_task_lifecycle_queued_to_blocked` — mock executor returns FAILURE (blocked)
  - [x] `test_task_lifecycle_worktree_cleaned_up_on_done` — verify worktree removed after success
  - [x] `test_task_lifecycle_worktree_cleaned_up_on_failure` — verify worktree removed after failure
  - [x] `test_task_lifecycle_run_yaml_has_mandatory_fields` — verify all FR50 fields present

- [x] Task 5: Verify everything passes (AC: all)
  - [x] Run `ruff check src/ tests/` — zero errors
  - [x] Run `mypy --strict src/` — zero errors
  - [x] Run `pytest -v` — all tests pass (77 existing + new)

## Dev Notes

### Critical Architecture Decisions

- **Constructor injection, no framework**: TaskRunner receives ALL dependencies as constructor parameters. This enables complete testability — integration tests inject mock executor, mock gates, real workspace.

- **GitWrapper for all git operations**: TaskRunner never calls `subprocess.run(["git", ...])` directly. All git operations go through GitWrapper (from Story 2.1).

- **State transitions via state_machine.transition()**: Every state change uses the pure `transition()` function. Invalid transitions raise `InvalidTransitionError`. This keeps state logic centralized.

- **try/finally for worktree cleanup**: The entire lifecycle is wrapped in try/finally. Even if an agent crashes or an exception propagates, the worktree is removed. No orphaned worktrees (NFR6).

- **ExitStatus.FAILURE maps to BLOCKED**: If the executor or reviewer returns `ExitStatus.FAILURE`, the task transitions to BLOCKED (agent couldn't proceed). If gates fail, the task transitions to FAILED (code quality issue). This distinction matters for the morning report.

### TaskRunner Implementation Pattern

```python
class TaskRunner:
    def __init__(self, executor, reviewer, gates, listener, workspace, config, git):
        ...

    def run(self, task_name, story, instructions, worktree_base) -> RunResult:
        branch = f"night/{task_name}"
        worktree = worktree_base / task_name
        started = datetime.now().isoformat()

        try:
            # QUEUED -> SETUP_WORKTREE
            state = transition(TaskState.QUEUED, TaskState.SETUP_WORKTREE)
            self.listener.on_status_change(task_name, TaskState.QUEUED, state)
            self.git.create_branch(branch)
            self.git.create_worktree(worktree, branch)

            # SETUP_WORKTREE -> IMPLEMENTATION
            state = transition(state, TaskState.IMPLEMENTATION)
            self.listener.on_status_change(...)
            process = self.executor.start(story, self.config, instructions)
            for line in self.executor.stream_output(process):
                self.listener.on_progress(task_name, "implementation", line)
            exit_status = self.executor.get_exit_status(process)

            if exit_status != ExitStatus.SUCCESS:
                # -> BLOCKED
                ...

            # IMPLEMENTATION -> REVIEW
            # ... similar pattern with reviewer

            # REVIEW -> GATES
            gate_results = self.gates.run_all(worktree)
            if gate_results.passed:
                # -> DONE
            else:
                # -> FAILED

        except Exception:
            # -> FAILED on any unhandled error
            ...
        finally:
            # Always clean up worktree
            try:
                self.git.remove_worktree(worktree)
            except HpncError:
                pass  # Best effort cleanup
```

### task-spec.yaml Format (for __main__.py)

```yaml
story: stories/login-validation.md
worktree_base: /tmp/hpnc-night
task_name: login-validation
executor: mock
reviewer: mock
config: _hpnc/config.yaml
instructions: _hpnc/executor-instructions.md
run_dir: _hpnc/runs/2026/04/06/001_login-validation
```

### Import Rules

- `core/task_runner.py` may import from: `core/state_machine.py`, `agents/base.py` (ExitStatus), `gates/runner.py` (GateRunner, GateResults), `events/base.py` (RunResult, TaskEventListener), `infra/` (Workspace, GitWrapper, Config, HpncError)
- `core/__main__.py` may import from: all `core/`, `agents/`, `gates/`, `events/`, `infra/`

### Previous Story Intelligence

- **Workspace** (2.1): fully implemented, atomic writes
- **GitWrapper** (2.1): create_branch, create_worktree, remove_worktree — all tested with real git
- **GateRunner** (2.2): run_all returns GateResults, never short-circuits, FileNotFoundError handled
- **FileEventListener** (2.3): on_status_change writes run.yaml, on_complete writes all fields
- **MockAgentExecutor** (1.3): configurable status/delay/file_changes, real Popen
- **State machine** (1.2): transition() function, InvalidTransitionError
- **tmp_workspace** fixture: real git repo with _hpnc/config.yaml
- **mock_executor_factory** fixture: parameterized mock creation
- **77 existing tests** — must not regress

### References

- [Source: architecture.md#Testability] — constructor injection, no globals
- [Source: architecture.md#Dispatcher ↔ Task-Runner Communication] — task-spec.yaml
- [Source: architecture.md#Process Management] — subprocess execution
- [Source: architecture.md#Data Flow] — complete pipeline
- [Source: epics.md#Story 2.4] — acceptance criteria
- [Source: prd.md#Task Lifecycle] — FR35-FR52

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- ruff auto-fixed datetime.UTC alias (UP017)

### Completion Notes List

- TaskRunner: complete lifecycle with constructor injection (7 deps + 2 name params)
- States: QUEUED -> SETUP_WORKTREE -> IMPLEMENTATION -> REVIEW -> GATES -> DONE/FAILED/BLOCKED
- try/finally ensures worktree cleanup, error handlers wrapped in try/except for cascading failure protection
- core/__main__.py entry point reads task-spec.yaml
- 6 integration tests: done/failed/blocked, worktree cleanup, run.yaml mandatory fields
- 83 total tests at time of completion

### Change Log

- 2026-04-06: Story 2.4 implementation complete
- 2026-04-06: Epic 2 review fixes — error handler, RunResult names, GateRunner exception safety

### File List

- src/hpnc/core/task_runner.py (created)
- src/hpnc/core/__main__.py (replaced stub)
- src/hpnc/core/__init__.py (modified — added TaskRunner)
- tests/integration/test_task_lifecycle.py (created)
