---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories, step-04-final-validation]
status: complete
completedAt: '2026-04-06'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/planning-artifacts/architecture.md
---

# hpnc - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for hpnc, decomposing the requirements from the PRD and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

**Project Setup & Configuration**
- FR1: Developer can initialize a new HPNC project in an existing repository (`hpnc init`)
- FR2: System can detect and verify connectivity to Claude Code CLI
- FR3: System can detect and verify connectivity to Codex CLI
- FR4: System can detect existing BMAD configuration in the project
- FR5: System can generate a default `_hpnc/config.yaml` with sensible defaults
- FR6: Developer can modify project configuration via YAML file
- FR7: System can locate the project root by searching upward for `_hpnc/config.yaml`
- FR8: System provides shell completion for commands, subcommands, flags, and story file paths (bash/zsh/fish)

**Story & Queue Management**
- FR9: Developer can add a story file to the night queue (`hpnc queue add`)
- FR10: Developer can remove a story from the night queue (Phase 2)
- FR11: Developer can reorder stories in the night queue (Phase 2)
- FR12: System can read and parse `night-queue.yaml` including task groups and priorities
- FR13: System can parse story frontmatter to extract night-ready metadata (executor, reviewer, risk, tests_required, touches, etc.)
- FR14: System can evaluate `depends_on` relationships between tasks (Phase 2)
- FR15: System can evaluate `release_policy` for task groups (Phase 2)
- FR16: System can define and expose the night-ready frontmatter schema as a machine-readable specification
- FR17: System can consume any story file that conforms to the night-ready frontmatter schema, regardless of how it was created

**Validation & Pre-flight**
- FR18: Developer can run a pre-flight validation check (`hpnc validate`)
- FR19: System can verify that all queued stories have `night_ready: true`
- FR20: System can verify that all mandatory frontmatter fields are present
- FR21: System can verify that `blocking_questions` is empty for each story
- FR22: System can verify that `tests_required` is defined for each story
- FR23: System can verify that Git worktrees can be created
- FR24: System can verify that a secrets hook (git-secrets/gitleaks) is active
- FR25: System can report validation failures with actionable guidance
- FR26: System can verify dev server, DB connection, port availability, disk space (Phase 2)

**Night Run Execution**
- FR27: Developer can start a night run immediately (`hpnc start`)
- FR28: Developer can schedule a night run for a specific time (`hpnc start --at`)
- FR29: Developer can schedule a night run with a delay (`hpnc start --delay`)
- FR30: Developer can simulate a night run without executing agents (`hpnc start --dry-run`)
- FR31: Developer can run the night queue with mock agents (`hpnc start --mock`)
- FR32: System can process queued tasks sequentially
- FR33: System can persist dispatcher state after each task completion
- FR34: System can clean up completed tasks from the queue

**Task Lifecycle & State Management**
- FR35: System can create a named branch (`night/<task-name>`) and manage worktree lifecycle (create, cleanup, handle orphaned worktrees)
- FR36: System can transition tasks through the state machine: queued -> implementation -> review -> gates -> terminal status
- FR37: System can invoke an AI agent for task implementation via AgentExecutor
- FR38: System can invoke a different AI agent for task review via AgentExecutor
- FR39: System can transition tasks to `done` when all gates pass
- FR40: System can transition tasks to `failed` when gates fail
- FR41: System can transition tasks to `blocked` when the agent cannot proceed without human input
- FR42: System can mark tasks as `proposal` when implementation is complete but human review is required before merge (Phase 2)
- FR43: System can mark tasks as `interrupted` when the process terminates unexpectedly (Phase 2)
- FR44: System can execute a fix-loop with configurable retry attempts (Phase 2)
- FR45: System can swap the executor role after configurable failed attempts (Phase 2)
- FR46: System can detect and handle API rate limits by pausing and resuming (Phase 2)
- FR47: System can enforce task timeout and detect agent inactivity (Phase 2)
- FR48: System can detect interrupted runs on startup and mark them correctly (Phase 2)
- FR49: System can clean up worktrees after task completion
- FR50: System can write `run.yaml` with mandatory fields: status, executor, reviewer, branch, started, finished, files_changed, story_source
- FR51: System can write `cost.json` with token usage per task (Phase 2)
- FR52: System can write `review.md` with structured review findings (Phase 2)

**Quality Assurance & Gates**
- FR53: System can execute build verification as a quality gate
- FR54: System can execute test suite as a quality gate
- FR55: System can execute linting as a quality gate
- FR56: System can verify that protected paths were not modified (Phase 2)
- FR57: System can verify that no secrets were committed (via pre-commit hook)
- FR58: System can auto-merge task branch into target branch when all gates pass and merge_policy is `done` (Phase 2)

**Reporting & Morning Review**
- FR59: Developer can view a summary of the last night run (`hpnc status`)
- FR60: System can generate a markdown report with task results, durations, and statuses
- FR61: System can display blocked tasks with recommended next actions
- FR62: System can display failed tasks with clear failure reasons
- FR63: Developer can view detailed information for a specific task (`hpnc show`) (Phase 2)
- FR64: Developer can view code changes for a specific task (`hpnc diff`) (Phase 2)
- FR65: Developer can view historical run data (`hpnc history`) (Phase 2)
- FR66: Developer can view token cost data over time (`hpnc costs`) (Phase 2)
- FR67: System can commit run artifacts into the task branch
- FR68: Developer can view and modify HPNC configuration via CLI (`hpnc config`) (Phase 2)

**Agent Orchestration**
- FR69: System can start an AI agent with story file, project config, and executor instructions
- FR70: System can stream or buffer agent output for logging
- FR71: System can capture agent exit status (success/failure/timeout)
- FR72: System can route tasks to specific agents based on story frontmatter (`executor` field)
- FR73: System can route reviews to specific agents based on story frontmatter (`reviewer` field)
- FR74: Developer can configure mock agent responses (status, delay, simulated file changes) for testing
- FR75: System provides an AgentExecutor interface that supports adding new agent types

**Logging & Observability**
- FR76: System can log dispatcher activities at configurable verbosity levels (minimal, normal, verbose)
- FR77: System can capture and store agent output (full, truncated, or none, configurable per config)

**BMAD Integration**
- FR78: BMad Builder can generate night-ready story templates based on the HPNC frontmatter schema (Phase 2)
- FR79: BMad Builder can validate stories against the night-ready schema before marking them ready (Phase 2)

**Documentation**
- FR80: System provides a MkDocs documentation site with Material Design theme, bilingual (German and English)
- FR81: System provides built-in CLI help (`--help`) for all commands with usage examples (auto-generated by Typer/Click)
- FR82: System provides an LLM-optimized context file (`HPNC.md`) generated from MkDocs sources
- FR83: System provides a separate project-specific `executor-instructions.md` with strict rules for autonomous night execution
- FR84: Documentation site covers: getting started, concepts, CLI reference, configuration reference, frontmatter schema, and troubleshooting

**Human Review Workflow (Phase 2)**
- FR85: Developer can configure a task's `merge_policy` as `proposal` to require human review before merge (Phase 2)
- FR86: System can generate human review instructions for `proposal`-status tasks (Phase 2)
- FR87: Developer can approve or reject a `proposal`-status task via CLI (Phase 2)
- FR88: System merges a `proposal` task only after explicit human approval (Phase 2)
- FR89: Morning report clearly surfaces `proposal` tasks that await human review (Phase 2)

### NonFunctional Requirements

**Reliability**
- NFR1: System must never silently discard, ignore, or fail to report a task error
- NFR2: System must persist dispatcher state to disk after every state transition
- NFR3: System must detect its own unexpected termination on next startup and mark affected tasks as `interrupted`
- NFR4: System must not corrupt Git repository state under any failure condition
- NFR5: System must log all significant events with timestamps, even at `minimal` verbosity
- NFR6: System must gracefully handle agent process crashes without leaving orphaned worktrees or locked files

**Data Integrity**
- NFR7: System must never auto-merge a branch unless all quality gates have verifiably passed
- NFR8: Run artifacts must accurately reflect the actual task outcome
- NFR9: System must not modify files outside the task's worktree during execution
- NFR10: Queue cleanup must only remove tasks that have reached a terminal state
- NFR11: All persisted files must use atomic writes (write to temp file, then rename)

**Recoverability**
- NFR12: After a crash, the next `hpnc start` must work without manual intervention
- NFR13: Recovery must preserve all information about completed tasks

**Idempotency**
- NFR14: Running `hpnc start` while a dispatcher is already running must be detected and rejected
- NFR15: `hpnc validate` must be a pure read-only operation
- NFR16: `hpnc init` in an already-initialized project must not overwrite existing configuration

**Graceful Degradation**
- NFR17: If any required agent is not reachable, system must refuse to run

**Security**
- NFR18: Agents must not have write access to protected paths
- NFR19: System must verify that a secrets pre-commit hook is active before starting any night run
- NFR20: Agent credentials must never be logged, stored in run artifacts, or committed to Git

**Performance**
- NFR21: CLI commands must complete within 2 seconds under normal conditions
- NFR22: Dispatcher overhead must add less than 60 seconds to a night run
- NFR23: State file writes must complete within 1 second

**Error Messages**
- NFR24: Every error message must contain: (1) what happened, (2) why, (3) what to do

**Integration**
- NFR25: System must work with any Git repository that supports worktrees (Git 2.20+)
- NFR26: AgentExecutor must isolate all CLI-specific behavior behind the abstraction
- NFR27: System must not depend on specific BMAD version or features

**Cross-Platform**
- NFR28: Phase 1 must run reliably on Windows 10/11
- NFR29: All file paths must use platform-independent handling (`pathlib`)
- NFR30: System must handle Windows-specific constraints: long paths, file locking, case-insensitive FS

**Documentation Quality**
- NFR31: Documentation must be kept in sync with implementation
- NFR32: `HPNC.md` must be regenerable from MkDocs sources via a single command

### Additional Requirements

**Starter Template**
- Architecture specifies `uv init --package --python 3.12` as the project initialization method
- Walking Skeleton as first implementation story (complete directory structure with stub interfaces)

**Implementation Waves (from Architecture)**
- Wave 1: Walking Skeleton + `infra/` + `schemas/` — Foundation, all interfaces as stubs (zero tokens)
- Wave 2: `core/state_machine.py` + `agents/mock.py` — Testable core logic (zero tokens)
- Wave 3: `gates/` + `core/task_runner.py` — Single task runs locally with mock (zero tokens)
- Wave 4: `core/dispatcher.py` + `core/validator.py` + `core/queue_manager.py` — Full night run with mock (zero tokens)
- Wave 5: `reporting/` + `cli/` — HPNC usable end-to-end with `--mock` (zero tokens)
- Wave 6: `agents/claude_code.py` + `agents/codex.py` — Real agent integration (tokens needed)

**Architectural Patterns (mandatory)**
- Constructor injection for all components (no DI framework, no globals)
- Protocol-based interfaces (`AgentExecutor`, `TaskEventListener`, `Gate`)
- Workspace abstraction for all file I/O (atomic writes via write-to-temp-then-rename)
- ProcessLock for dispatcher (prevents double-start, NFR14)
- TaskEventListener pattern for all status updates
- HpncError hierarchy with what/why/action fields (NFR24)
- State Machine as independent module (pure logic, no I/O)
- Strict layered architecture: cli -> core -> agents/gates/events -> infra
- No global singletons, no `print()`, no `shell=True`, no bare `Exception`

**Conventions (mandatory)**
- PEP 8 naming, Google-Style docstrings, `mypy --strict`
- Conventional Commits for all commit messages
- Test naming: `test_<what>_<when>_<expected>`
- `ruff` for linting/formatting, pre-commit hooks
- `__all__` in every `__init__.py`

### UX Design Requirements

N/A — CLI-only tool with console output (Rich-formatted). No UI or UX design document applicable.

### FR Coverage Map

FR1: Epic 3 — hpnc init
FR2: Epic 3 — Detect Claude Code CLI connectivity
FR3: Epic 3 — Detect Codex CLI connectivity
FR4: Epic 3 — Detect existing BMAD configuration
FR5: Epic 3 — Generate default config.yaml
FR6: Epic 3 — Modify config via YAML
FR7: Epic 1 — Project root discovery (ConfigLoader)
FR8: Epic 1 — Shell completion (Typer auto-generated)
FR9: Epic 3 — hpnc queue add
FR10: Phase 2
FR11: Phase 2
FR12: Epic 3 — Parse night-queue.yaml
FR13: Epic 3 — Parse story frontmatter
FR14: Phase 2
FR15: Phase 2
FR16: Epic 1 — Frontmatter schema definition
FR17: Epic 3 — Consume conformant story files
FR18: Epic 3 — hpnc validate
FR19: Epic 3 — Verify night_ready: true
FR20: Epic 3 — Verify mandatory frontmatter fields
FR21: Epic 3 — Verify blocking_questions empty
FR22: Epic 3 — Verify tests_required defined
FR23: Epic 3 — Verify Git worktrees available
FR24: Epic 3 — Verify secrets hook active
FR25: Epic 3 — Report validation failures with guidance
FR26: Phase 2
FR27: Epic 4 — hpnc start
FR28: Epic 4 — hpnc start --at
FR29: Epic 4 — hpnc start --delay
FR30: Epic 4 — hpnc start --dry-run
FR31: Epic 4 — hpnc start --mock
FR32: Epic 4 — Process queued tasks sequentially
FR33: Epic 4 — Persist dispatcher state
FR34: Epic 4 — Clean up completed tasks
FR35: Epic 2 — Worktree lifecycle (create branch, worktree, cleanup)
FR36: Epic 2 — State machine transitions
FR37: Epic 2 — Invoke agent for implementation (mock)
FR38: Epic 2 — Invoke agent for review (mock)
FR39: Epic 2 — Transition to done when gates pass
FR40: Epic 2 — Transition to failed when gates fail
FR41: Epic 2 — Transition to blocked
FR42: Phase 2
FR43: Phase 2
FR44: Phase 2
FR45: Phase 2
FR46: Phase 2
FR47: Phase 2
FR48: Phase 2
FR49: Epic 2 — Worktree cleanup after completion
FR50: Epic 2 — Write run.yaml with mandatory fields
FR51: Phase 2
FR52: Phase 2
FR53: Epic 2 — Build verification gate
FR54: Epic 2 — Test suite gate
FR55: Epic 2 — Lint gate
FR56: Phase 2
FR57: Epic 2 — Secrets verification (pre-commit hook)
FR58: Phase 2
FR59: Epic 4 — hpnc status
FR60: Epic 4 — Generate markdown report
FR61: Epic 4 — Display blocked tasks with next actions
FR62: Epic 4 — Display failed tasks with reasons
FR63: Phase 2
FR64: Phase 2
FR65: Phase 2
FR66: Phase 2
FR67: Epic 4 — Commit run artifacts into task branch
FR68: Phase 2
FR69: Epic 2 — Start agent with story + config + instructions
FR70: Epic 2 — Stream/buffer agent output
FR71: Epic 2 — Capture agent exit status
FR72: Epic 5 — Route tasks to specific agents
FR73: Epic 5 — Route reviews to specific agents
FR74: Epic 1 — Mock agent responses configuration
FR75: Epic 1 — AgentExecutor interface
FR76: Epic 2 — Dispatcher logging at configurable verbosity
FR77: Epic 2 — Agent output capture
FR78: Phase 2
FR79: Phase 2
FR80: Epic 6 — MkDocs site bilingual (de/en)
FR81: Epic 1 — CLI --help (Typer auto-generated)
FR82: Epic 6 — HPNC.md LLM context file
FR83: Epic 6 — executor-instructions.md template
FR84: Epic 6 — Documentation site content
FR85: Phase 2
FR86: Phase 2
FR87: Phase 2
FR88: Phase 2
FR89: Phase 2

## Epic List

### Epic 1: Project Foundation — "hpnc existiert"
HPNC is installable as a Python package via pip/pipx, `hpnc --help` shows all commands (as stubs), CI pipeline runs green, the core state machine is implemented and tested, MockAgentExecutor is ready, and all Protocol interfaces are defined as stubs. This is the Walking Skeleton that enables all subsequent development.
**FRs covered:** FR7, FR8, FR16, FR74, FR75, FR81
**NFRs addressed:** NFR24 (error hierarchy), NFR28-30 (cross-platform from day 1)

### Epic 2: Task Execution Engine — "Tasks werden verarbeitet"
A single task can be processed through the complete state machine lifecycle using mock agents: worktree creation, implementation (mock), review (mock), quality gates (build/test/lint), and terminal status (done/failed/blocked). run.yaml is written with all mandatory fields. Everything is token-free testable.
**FRs covered:** FR35-FR41, FR49-FR50, FR53-FR55, FR57, FR69-FR71, FR76-FR77
**NFRs addressed:** NFR1-6 (reliability), NFR7-11 (data integrity)

### Epic 3: Setup, Validation & Queue — "Bereit für die Nacht"
Developer can `hpnc init` (config generation, connectivity check, BMAD detection), `hpnc queue add` (add stories to night queue), and `hpnc validate` (pre-flight check: frontmatter, blocking_questions, tests_required, worktree availability, secrets hook). The complete preparation workflow works.
**FRs covered:** FR1-FR6, FR9, FR12-FR13, FR17-FR25
**NFRs addressed:** NFR14-16 (idempotency), NFR17 (graceful degradation)

### Epic 4: Night Run & Morning Review — "Der Nachtzyklus"
Developer can `hpnc start` (immediate, --at, --delay, --dry-run, --mock), the dispatcher processes the queue sequentially, persists state after each task, and `hpnc status` shows the morning report with task results, blocked/failed explanations, and recommended next actions. The complete overnight workflow works end-to-end with mock agents.
**FRs covered:** FR27-FR34, FR59-FR62, FR67
**NFRs addressed:** NFR12-13 (recoverability), NFR21-23 (performance)

### Epic 5: Real Agent Integration — "KI arbeitet über Nacht"
ClaudeCodeExecutor and CodexExecutor are implemented. Real AI agents execute tasks autonomously. Agent routing based on story frontmatter (executor/reviewer fields) works. The system transitions from mock to production.
**FRs covered:** FR2-FR3 (real connectivity), FR72-FR73
**NFRs addressed:** NFR17-20 (security), NFR25-27 (integration)

### Epic 6: Documentation — "Alles dokumentiert"
Bilingual MkDocs site (de/en) with Material Design theme, HPNC.md as LLM-optimized context file generated from MkDocs sources, executor-instructions.md template, and full documentation covering concepts, CLI reference, configuration, frontmatter schema, and troubleshooting.
**FRs covered:** FR80, FR82-FR84
**NFRs addressed:** NFR31-32 (documentation quality)

## Epic 1: Project Foundation — "hpnc existiert"

HPNC is installable as a Python package via pip/pipx, `hpnc --help` shows all commands (as stubs), CI pipeline runs green, the core state machine is implemented and tested, MockAgentExecutor is ready, and all Protocol interfaces are defined as stubs. This is the Walking Skeleton that enables all subsequent development.

### Story 1.1: Project Bootstrap & Package Structure

As a developer,
I want to initialize the HPNC project with uv as a properly structured Python package,
So that the project is installable, `hpnc --help` works, and all development tooling is configured.

**Acceptance Criteria:**

**Given** an empty repository
**When** the project is initialized with `uv init --package --python 3.12`
**Then** `pyproject.toml` exists with project metadata, dependencies (typer, rich, pyyaml), and dev dependencies (pytest, pytest-cov, ruff, mypy)
**And** the complete `src/hpnc/` directory structure exists with all subdirectories (`cli/`, `core/`, `agents/`, `gates/`, `reporting/`, `events/`, `infra/`, `schemas/`)
**And** every `__init__.py` contains an `__all__` export list
**And** `src/hpnc/__main__.py` and `src/hpnc/core/__main__.py` exist as entry points
**And** `src/hpnc/py.typed` marker exists (PEP 561)
**And** `ruff` and `mypy` are configured in `pyproject.toml`
**And** `.pre-commit-config.yaml` is configured with ruff and mypy hooks
**And** `.gitignore` covers Python, uv, and IDE artifacts
**And** `LICENSE` exists with MIT license
**And** `hpnc --help` displays Typer-generated help showing all command stubs (init, validate, start, status, queue)
**And** shell completion is available for bash, zsh, and fish via Typer (FR8)
**And** `ruff check` and `mypy --strict` pass with zero errors
**And** `tests/` directory structure mirrors `src/hpnc/` with `conftest.py` files

### Story 1.2: Core Interfaces, State Machine & Error Hierarchy

As a developer,
I want all Protocol interfaces, the state machine, the frontmatter schema, and the error hierarchy defined,
So that every subsequent module can be developed against stable interfaces with a tested core.

**Acceptance Criteria:**

**Given** the project structure from Story 1.1
**When** core interfaces and types are implemented
**Then** `AgentExecutor` Protocol exists in `agents/base.py` with 3 methods: `start()`, `stream_output()`, `get_exit_status()` (FR75)
**And** `TaskEventListener` Protocol exists in `events/base.py` with methods: `on_status_change()`, `on_progress()`, `on_complete()`
**And** `TaskState` Enum in `core/state_machine.py` contains all Phase 1 states (QUEUED, SETUP_WORKTREE, IMPLEMENTATION, REVIEW, GATES, DONE, FAILED, BLOCKED) and Phase 2 labels (FIX_ATTEMPT, PAUSED, AWAITING_REVIEW, PROPOSAL, MERGED, INTERRUPTED)
**And** Phase 1 transition table is implemented as a pure function (no I/O, no dependencies)
**And** invalid state transitions raise an appropriate error
**And** `HpncError` base class exists in `infra/errors.py` with `what`, `why`, `action` fields (NFR24)
**And** subclasses exist: `ConfigError`, `ConnectivityError`, `ValidationError`, `TaskBlockedError`, `TaskInterruptedError` with mapped exit codes (0-5)
**And** frontmatter schema is defined in `schemas/frontmatter.py` with all night-ready fields (night_ready, executor, reviewer, risk, tests_required, touches, blocking_questions, gates_required) (FR16)
**And** `ConfigLoader` stub exists in `infra/config.py` with `find_root()` method signature (FR7)
**And** `Workspace` stub exists in `infra/workspace.py` with method signatures for `read_yaml()`, `write_yaml_atomic()`, `read_markdown()`
**And** unit tests exist for all state machine transitions (`test_state_machine_queued_to_setup_worktree_succeeds`, invalid transition test, all Phase 1 paths)
**And** unit tests exist for HpncError hierarchy (correct exit codes, format)
**And** all paths use `pathlib.Path`, never `str` (NFR29)

### Story 1.3: Mock Executor & CI Pipeline

As a developer,
I want a configurable MockAgentExecutor and a CI pipeline,
So that the entire system can be tested token-free and every commit is validated automatically.

**Acceptance Criteria:**

**Given** the interfaces from Story 1.2
**When** MockAgentExecutor is implemented in `agents/mock.py`
**Then** `MockAgentExecutor` implements the `AgentExecutor` Protocol (FR74)
**And** mock responses are configurable: exit status (success, failure, timeout), delay duration, and simulated file changes
**And** mock can simulate writing files to a worktree directory
**And** default configuration returns `ExitStatus.SUCCESS` with zero delay
**And** `FileEventListener` stub exists in `events/file_listener.py` implementing `TaskEventListener`
**And** `.github/workflows/ci.yml` exists with jobs for: ruff check, mypy --strict, pytest (unit + integration)
**And** CI pipeline uses uv for dependency installation and caching
**And** CI runs on both Ubuntu and Windows runners (NFR28)
**And** all existing tests pass in CI
**And** unit tests verify MockAgentExecutor with different configurations (success, failure, timeout)
**And** `ruff check`, `mypy --strict`, and `pytest` all pass locally and in CI

## Epic 2: Task Execution Engine — "Tasks werden verarbeitet"

A single task can be processed through the complete state machine lifecycle using mock agents: worktree creation, implementation (mock), review (mock), quality gates (build/test/lint), and terminal status (done/failed/blocked). run.yaml is written with all mandatory fields. Everything is token-free testable.

### Story 2.1: Workspace & Git Infrastructure

As a developer,
I want a Workspace abstraction for atomic file operations and a Git subprocess wrapper,
So that all file I/O is safe against crashes and worktree operations are isolated behind a testable interface.

**Acceptance Criteria:**

**Given** the project structure from Epic 1
**When** Workspace and Git infrastructure are implemented
**Then** `Workspace` in `infra/workspace.py` provides `read_yaml(path)`, `write_yaml_atomic(path, data)`, and `read_markdown(path)` (NFR11)
**And** `write_yaml_atomic` writes to a temp file first, then renames (atomic write pattern)
**And** `Workspace` accepts a `root` parameter (project root in production, tmp directory in tests)
**And** Git wrapper in `infra/git.py` provides methods for: `create_worktree()`, `remove_worktree()`, `create_branch()`, `list_worktrees()`, `checkout_branch()`
**And** Git wrapper uses `subprocess.run()` with `capture_output=True` and never `shell=True`
**And** all methods use `pathlib.Path` for path arguments (NFR29)
**And** Git operations handle Windows-specific constraints: long paths, case-insensitive FS (NFR30)
**And** `ProcessLock` in `infra/process_lock.py` provides cross-platform file locking for dispatcher exclusivity (NFR14)
**And** `conftest.py` provides `tmp_workspace` fixture creating a temporary HPNC workspace
**And** unit tests verify atomic write behavior (write succeeds, partial write doesn't corrupt)
**And** unit tests verify Git wrapper with a real temporary Git repository
**And** unit tests verify ProcessLock (acquire, release, double-lock detection)
**And** `tmp_workspace` fixture creates a complete HPNC workspace structure (`_hpnc/config.yaml`, `_hpnc/night-queue.yaml`, valid Git repo with at least one commit) that mirrors production layout
**And** `mock_executor` fixture is reusable with parameterized configurations (via factory pattern or `pytest.fixture` params)
**And** fixture usage is documented in `tests/conftest.py` with docstrings explaining intended usage patterns

### Story 2.2: Quality Gates

As a developer,
I want quality gates that verify build, tests, and lint pass in a worktree,
So that no task reaches `done` status without passing automated quality checks.

**Acceptance Criteria:**

**Given** the Workspace abstraction from Story 2.1
**When** quality gates are implemented in `gates/`
**Then** `Gate` Protocol exists in `gates/runner.py` with a `run(worktree: Path) -> GateResult` method
**And** `BuildGate` in `gates/build.py` executes the project's build command and returns pass/fail (FR53)
**And** `TestGate` in `gates/tests.py` executes the project's test command and returns pass/fail (FR54)
**And** `LintGate` in `gates/lint.py` executes the project's lint command and returns pass/fail (FR55)
**And** `GateRunner` in `gates/runner.py` executes all gates sequentially and returns aggregated `GateResults`
**And** gate commands are configurable (not hardcoded to specific tools)
**And** secrets verification checks that a pre-commit hook (git-secrets or gitleaks) is active (FR57)
**And** a false-positive gate pass is impossible — gates only return pass when subprocess exit code is 0 (NFR7)
**And** gate failures include the gate name, exit code, and stderr output for diagnosis
**And** unit tests verify each gate with mock subprocess results (pass, fail, timeout)
**And** unit tests verify GateRunner aggregation logic
**And** gate tests use `tmp_workspace` from Story 2.1 to validate fixture provides a complete, production-like workspace (valid Git repo, _hpnc/config.yaml, working worktree) — if fixture is insufficient, fix it in conftest.py before proceeding

### Story 2.3: Event System & Logging

As a developer,
I want a TaskEventListener that persists status changes to run.yaml and configurable logging,
So that every state transition is recorded and the night run is fully observable.

**Acceptance Criteria:**

**Given** the Workspace abstraction from Story 2.1
**When** the event system and logging are implemented
**Then** `FileEventListener` in `events/file_listener.py` implements `TaskEventListener` Protocol
**And** `on_status_change()` writes the new status to `run.yaml` via `Workspace.write_yaml_atomic()` (NFR2)
**And** `on_progress()` appends progress detail to the run log
**And** `on_complete()` writes final `RunResult` to `run.yaml` with all mandatory fields (FR50)
**And** every status transition is persisted to disk immediately — no batching (NFR2)
**And** logging setup in `infra/logging.py` uses stdlib `logging` with Rich handler for terminal output
**And** `logging.FileHandler` writes to run-specific log files
**And** verbosity is configurable: minimal, normal, verbose (FR76)
**And** agent output capture supports full, truncated, or none modes (FR77)
**And** log format includes timestamps at all verbosity levels (NFR5)
**And** unit tests verify FileEventListener writes correct YAML structure
**And** unit tests verify logging configuration at each verbosity level

### Story 2.4: Task Runner — Complete Lifecycle

As a developer,
I want a Task Runner that processes a single task through the complete state machine lifecycle,
So that a task can autonomously move from queued to done/failed/blocked using mock agents.

**Acceptance Criteria:**

**Given** Workspace, Git, Gates, EventListener, and MockAgentExecutor from previous stories
**When** Task Runner is implemented in `core/task_runner.py`
**Then** Task Runner receives dependencies via constructor injection: `executor`, `reviewer` (AgentExecutor), `gates` (GateRunner), `listener` (TaskEventListener), `workspace` (Workspace), `config` (Config)
**And** Task Runner creates a named branch `night/<task-name>` and a Git worktree for the task (FR35)
**And** Task Runner transitions through states: QUEUED -> SETUP_WORKTREE -> IMPLEMENTATION -> REVIEW -> GATES -> terminal (FR36)
**And** during IMPLEMENTATION, Task Runner invokes the executor AgentExecutor with story, config, and instructions (FR37, FR69)
**And** agent output is streamed/buffered via AgentExecutor (FR70)
**And** agent exit status is captured (FR71)
**And** during REVIEW, Task Runner invokes a different AgentExecutor instance for review (FR38)
**And** if all gates pass, task transitions to DONE (FR39)
**And** if any gate fails, task transitions to FAILED with gate failure details (FR40)
**And** if the agent signals it cannot proceed, task transitions to BLOCKED with reason (FR41)
**And** worktree is cleaned up after task completion regardless of terminal status (FR49)
**And** `run.yaml` is written with mandatory fields: status, executor, reviewer, branch, started, finished, files_changed, story_source (FR50)
**And** every state transition fires the TaskEventListener (NFR2)
**And** agent crashes are handled gracefully without orphaned worktrees (NFR6)
**And** files outside the worktree are never modified (NFR9)
**And** integration tests verify complete lifecycle: queued -> done (with mock success)
**And** integration tests verify complete lifecycle: queued -> failed (with mock gate failure)
**And** integration tests verify complete lifecycle: queued -> blocked (with mock block signal)
**And** Task Runner is independently executable via `python -m hpnc.core.task_runner`

## Epic 3: Setup, Validation & Queue — "Bereit für die Nacht"

Developer can `hpnc init` (config generation, connectivity check, BMAD detection), `hpnc queue add` (add stories to night queue), and `hpnc validate` (pre-flight check: frontmatter, blocking_questions, tests_required, worktree availability, secrets hook). The complete preparation workflow works.

### Story 3.1: Config Loader & Project Root Discovery

As a developer,
I want HPNC to find my project root automatically and load configuration with sensible defaults,
So that all `hpnc` commands work from any subdirectory within my project.

**Acceptance Criteria:**

**Given** a project with `_hpnc/config.yaml` in the root
**When** `ConfigLoader.find_root()` is called from any subdirectory
**Then** it searches upward from the current working directory until it finds `_hpnc/config.yaml` (FR7)
**And** if no `_hpnc/config.yaml` is found, a `ConfigError` is raised with what/why/action explaining how to run `hpnc init`

**Given** a valid `_hpnc/config.yaml`
**When** `ConfigLoader.load()` is called
**Then** YAML is parsed and merged with built-in defaults (merge_target: develop, timeout: 30m, max_fix_attempts: 3, etc.) (FR5, FR6)
**And** missing optional fields use defaults, missing mandatory fields raise `ConfigError`
**And** the resulting `Config` object provides typed access to all configuration values
**And** all paths in config are resolved as `pathlib.Path` relative to project root (NFR29)

**Given** unit tests
**Then** tests verify upward search finds root from nested directories
**And** tests verify default merging behavior
**And** tests verify error for missing config file
**And** tests verify error for malformed YAML

### Story 3.2: hpnc init Command

As a developer,
I want to initialize HPNC in my existing repository with a single command,
So that I can start using HPNC with sensible defaults and verified connectivity.

**Acceptance Criteria:**

**Given** an existing Git repository without HPNC configuration
**When** the developer runs `hpnc init`
**Then** `_hpnc/` directory is created with `config.yaml` containing sensible defaults (FR1, FR5)
**And** `_hpnc/executor-instructions.md` is created with a template for agent rules
**And** `_hpnc/night-queue.yaml` is created as an empty queue file
**And** connectivity check verifies Claude Code CLI is installed and reachable via version check subprocess (FR2)
**And** connectivity check verifies Codex CLI is installed and reachable via version check subprocess (FR3)
**And** connectivity results are displayed with clear pass/fail indicators using Rich formatting
**And** if an agent CLI is not found, a warning is shown (not a fatal error — agents may be installed later)
**And** existing BMAD configuration is detected and reported (FR4)
**And** output confirms successful initialization with next steps guidance

**Given** `hpnc init` is run in an already-initialized project
**When** `_hpnc/config.yaml` already exists
**Then** existing configuration is not overwritten (NFR16)
**And** a message informs the developer that the project is already initialized
**And** connectivity check still runs and reports current status

**Given** unit/integration tests
**Then** tests verify directory and file creation in tmp workspace
**And** tests verify existing config is preserved on re-init
**And** tests verify connectivity check output for missing/present CLIs

### Story 3.3: Queue Manager & hpnc queue add

As a developer,
I want to add story files to the night queue via CLI,
So that I can prepare multiple tasks for overnight execution.

**Acceptance Criteria:**

**Given** an initialized HPNC project
**When** the developer runs `hpnc queue add stories/my-story.md`
**Then** the story file path is validated to exist and be a markdown file (FR9)
**And** story frontmatter is parsed to extract night-ready metadata: night_ready, executor, reviewer, risk, tests_required, touches, blocking_questions, gates_required (FR13)
**And** the story is added to `_hpnc/night-queue.yaml` with its metadata (FR12)
**And** confirmation message shows the story was added with key metadata summary

**Given** a story file that does not conform to the night-ready frontmatter schema
**When** the developer runs `hpnc queue add` with this file
**Then** the system accepts any story file that has valid frontmatter (FR17)
**And** missing optional fields use defaults from project config

**Given** the same story is added to the queue twice
**When** `hpnc queue add` is run with a duplicate story
**Then** the system warns about the duplicate and does not add it again

**Given** `_hpnc/night-queue.yaml` already contains entries
**When** a new story is added
**Then** the new story is appended to the existing queue, preserving order

**Given** unit tests
**Then** tests verify frontmatter parsing with valid and invalid story files
**And** tests verify queue YAML read/write/append operations
**And** tests verify duplicate detection
**And** tests use fixture story files from `tests/fixtures/stories/`

### Story 3.4: Validation Engine & hpnc validate

As a developer,
I want to run a pre-flight validation check before starting a night run,
So that I can be confident all stories are properly prepared and the environment is ready.

**Acceptance Criteria:**

**Given** an initialized HPNC project with stories in the queue
**When** the developer runs `hpnc validate` (FR18)
**Then** validation is a pure read-only operation — no files are modified (NFR15)

**Given** queued stories are validated
**When** validation checks run
**Then** every queued story is checked for `night_ready: true` (FR19)
**And** every queued story is checked for all mandatory frontmatter fields present (FR20)
**And** every queued story is checked for empty `blocking_questions` (FR21)
**And** every queued story is checked for defined `tests_required` (FR22)
**And** Git worktree availability is verified (can create worktrees, no conflicts) (FR23)
**And** secrets hook (git-secrets or gitleaks) is verified as active (FR24)
**And** if any required agent (Claude Code, Codex) is not reachable, validation fails with clear error (NFR17)

**Given** validation failures
**When** one or more checks fail
**Then** each failure is reported with actionable guidance: what failed, why, and what to do (FR25, NFR24)
**And** all failures are reported (not just the first one)
**And** exit code is 1 for validation errors

**Given** all checks pass
**When** validation succeeds
**Then** a green success message confirms readiness with summary of validated stories
**And** exit code is 0

**Given** unit/integration tests
**Then** tests verify each validation check independently (missing night_ready, missing fields, non-empty blocking_questions, etc.)
**And** tests verify actionable error messages contain what/why/action
**And** tests verify read-only behavior (no file modifications)
**And** tests use fixture stories with specific validation failures

## Epic 4: Night Run & Morning Review — "Der Nachtzyklus"

Developer can `hpnc start` (immediate, --at, --delay, --dry-run, --mock), the dispatcher processes the queue sequentially, persists state after each task, and `hpnc status` shows the morning report with task results, blocked/failed explanations, and recommended next actions. The complete overnight workflow works end-to-end with mock agents.

### Story 4.1: Dispatcher — Sequential Task Processing

As a developer,
I want a Dispatcher that processes queued tasks sequentially through the Task Runner,
So that multiple tasks can be executed in a single night run with state persisted between tasks.

**Acceptance Criteria:**

**Given** a night queue with one or more tasks
**When** the Dispatcher starts
**Then** it acquires the ProcessLock to prevent double-start (NFR14)
**And** it loads and parses `night-queue.yaml` via Queue Manager
**And** tasks are processed sequentially in queue order (FR32)
**And** for each task, a `task-spec.yaml` is written and Task Runner is started as subprocess
**And** dispatcher state is persisted to `_hpnc/dispatcher-state.yaml` after each task completion (FR33, NFR2)
**And** completed tasks (done, failed, blocked) are cleaned up from the queue (FR34)
**And** if the Dispatcher is interrupted, the next `hpnc start` detects stale state and recovers (NFR12)
**And** recovery preserves all information about previously completed tasks (NFR13)
**And** dispatcher overhead adds less than 60 seconds to a night run (NFR22)

**Given** a second `hpnc start` is attempted while a dispatcher is running
**When** the ProcessLock is already held
**Then** the second instance is rejected with a clear error message (NFR14)

**Given** integration tests with MockAgentExecutor
**Then** tests verify sequential processing of 2+ tasks
**And** tests verify state persistence after each task
**And** tests verify queue cleanup after terminal states
**And** tests verify lock acquisition and double-start rejection
**And** tests verify crash recovery (stale state detection)

### Story 4.2: Scheduling & hpnc start Command

As a developer,
I want to start a night run immediately or schedule it for later,
So that I can set up the run before going to bed and it starts at the right time.

**Acceptance Criteria:**

**Given** an initialized and validated HPNC project with stories in the queue
**When** the developer runs `hpnc start`
**Then** the Dispatcher starts immediately and processes the queue (FR27)

**Given** the `--at` flag is provided
**When** the developer runs `hpnc start --at 23:00`
**Then** the process calculates the delay and sleeps until the target time (FR28)
**And** on wake, it checks if the target time has passed (handles sleep/hibernate time jumps)
**And** if the target time is in the past, it starts immediately

**Given** the `--delay` flag is provided
**When** the developer runs `hpnc start --delay 30m`
**Then** the process waits for the specified duration before starting (FR29)

**Given** the `--dry-run` flag is provided
**When** the developer runs `hpnc start --dry-run`
**Then** the system simulates queue processing without executing agents — showing what would happen (FR30)
**And** no state files are modified, no worktrees are created

**Given** the `--mock` flag is provided
**When** the developer runs `hpnc start --mock`
**Then** the system uses MockAgentExecutor instead of real agents (FR31)
**And** the complete pipeline runs: queue processing, task lifecycle, gates, report generation

**Given** CLI requirements
**Then** `hpnc start` completes within 2 seconds (excluding agent execution time) (NFR21)
**And** Rich-formatted output shows progress indicators during queue processing
**And** exit codes follow the standard mapping (0 success, 1 error, 3 interrupted)

**Given** unit/integration tests
**Then** tests verify immediate start
**And** tests verify --dry-run produces no side effects
**And** tests verify --mock uses MockAgentExecutor
**And** tests verify scheduling delay calculation

### Story 4.3: Report Generator & hpnc status

As a developer,
I want to see a clear morning report of what happened last night,
So that I can quickly understand results and decide on next steps within minutes.

**Acceptance Criteria:**

**Given** a completed night run with run artifacts in `_hpnc/runs/`
**When** the developer runs `hpnc status` (FR59)
**Then** a markdown report is generated with: run date, task count, task table (name, executor, reviewer, status, duration) (FR60)
**And** the report is saved to `_hpnc/reports/` with date-based path

**Given** tasks with `blocked` status in the run
**When** the report is generated
**Then** blocked tasks show the blocking reason and a recommended next action prefixed with `->` (FR61)

**Given** tasks with `failed` status in the run
**When** the report is generated
**Then** failed tasks show the failure reason (which gate failed, exit code, stderr excerpt) and recommended next action (FR62)

**Given** run artifacts need to be preserved
**When** a task completes
**Then** run artifacts (run.yaml, dispatcher.log) are committed into the task branch (FR67)

**Given** the terminal display
**When** `hpnc status` runs
**Then** output is Rich-formatted with colored status indicators (green=done, red=failed, yellow=blocked)
**And** tables are properly aligned and readable
**And** the command completes within 2 seconds (NFR21)

**Given** no previous night run exists
**When** the developer runs `hpnc status`
**Then** a clear message informs that no night run results were found

**Given** unit/integration tests
**Then** tests verify report generation from fixture run data (mixed statuses)
**And** tests verify blocked task messaging includes reason + next action
**And** tests verify failed task messaging includes gate details
**And** tests verify report markdown formatting
**And** tests verify "no runs found" edge case

## Epic 5: Real Agent Integration — "KI arbeitet über Nacht"

ClaudeCodeExecutor and CodexExecutor are implemented. Real AI agents execute tasks autonomously. Agent routing based on story frontmatter (executor/reviewer fields) works. The system transitions from mock to production.

### Story 5.1: Claude Code Executor

As a developer,
I want HPNC to invoke Claude Code CLI for task implementation and review,
So that real AI-powered code generation runs autonomously in my worktrees.

**Acceptance Criteria:**

**Given** Claude Code CLI is installed and authenticated
**When** a task's frontmatter specifies `executor: opus` or `reviewer: opus`
**Then** `ClaudeCodeExecutor` in `agents/claude_code.py` implements the `AgentExecutor` Protocol
**And** `start()` launches Claude Code as subprocess with: story file path, project config, and executor-instructions.md (FR69)
**And** the subprocess working directory is set to the task's worktree
**And** `stream_output()` captures Claude Code's stdout/stderr for logging (FR70)
**And** `get_exit_status()` maps Claude Code's exit code to `ExitStatus` (success/failure/timeout) (FR71)
**And** agent routing selects ClaudeCodeExecutor when story frontmatter `executor` field is `opus` (FR72)
**And** agent routing selects ClaudeCodeExecutor when story frontmatter `reviewer` field is `opus` (FR73)
**And** all CLI-specific behavior is isolated within `claude_code.py` — no Claude Code details leak to Task Runner (NFR26)
**And** agent credentials are never logged, stored in run artifacts, or committed to Git (NFR20)
**And** connectivity verification uses Claude Code version check (FR2)
**And** if Claude Code is not reachable, a `ConnectivityError` is raised with what/why/action (NFR17)
**And** integration tests with MockAgentExecutor verify routing logic (executor: opus -> ClaudeCodeExecutor selected)

### Story 5.2: Codex Executor

As a developer,
I want HPNC to invoke Codex CLI for task implementation and review,
So that cross-model review works with a different AI reviewing the implementing model's output.

**Acceptance Criteria:**

**Given** Codex CLI is installed and authenticated
**When** a task's frontmatter specifies `executor: codex` or `reviewer: codex`
**Then** `CodexExecutor` in `agents/codex.py` implements the `AgentExecutor` Protocol
**And** `start()` launches Codex as subprocess with: story file path, project config, and review instructions
**And** the subprocess working directory is set to the task's worktree
**And** `stream_output()` captures Codex's stdout/stderr for logging (FR70)
**And** `get_exit_status()` maps Codex's exit code to `ExitStatus` (FR71)
**And** agent routing selects CodexExecutor when story frontmatter `executor` field is `codex` (FR72)
**And** agent routing selects CodexExecutor when story frontmatter `reviewer` field is `codex` (FR73)
**And** all CLI-specific behavior is isolated within `codex.py` (NFR26)
**And** agent credentials are never logged or stored (NFR20)
**And** connectivity verification uses Codex version check (FR3)
**And** if Codex is not reachable, a `ConnectivityError` is raised (NFR17)
**And** the default routing pattern (executor: opus, reviewer: codex) enables cross-model review
**And** integration tests verify routing logic (reviewer: codex -> CodexExecutor selected)
**And** integration test verifies end-to-end flow: executor=opus + reviewer=codex routes to correct executors

## Epic 6: Documentation — "Alles dokumentiert"

Bilingual MkDocs site (de/en) with Material Design theme, HPNC.md as LLM-optimized context file generated from MkDocs sources, executor-instructions.md template, and full documentation covering concepts, CLI reference, configuration, frontmatter schema, and troubleshooting.

### Story 6.1: MkDocs Documentation Site

As a developer,
I want a bilingual documentation site covering all HPNC concepts and CLI reference,
So that I have a comprehensive reference for setup, configuration, and troubleshooting.

**Acceptance Criteria:**

**Given** the HPNC project with all CLI commands implemented
**When** the documentation site is built
**Then** `docs/mkdocs.yml` configures MkDocs with Material Design theme and i18n support (FR80)
**And** German (`docs/de/`) and English (`docs/en/`) content directories exist with identical structure
**And** documentation covers: getting started guide, concepts (night-policy, story format, two-layer release model, state machine), CLI reference (init, validate, start, status, queue), configuration reference (config.yaml schema, all options), frontmatter schema reference, and troubleshooting (FR84)
**And** `mkdocs build` produces a complete static site without errors
**And** `mkdocs serve` provides a local preview with hot-reload
**And** MkDocs dependencies are added to dev dependencies in `pyproject.toml`

**Given** documentation quality requirements
**Then** all documented CLI commands match actual implementation behavior
**And** configuration reference documents all fields with defaults and examples
**And** frontmatter schema reference includes all fields, types, and validation rules
**And** troubleshooting covers common errors with solutions

### Story 6.2: HPNC.md & Executor Instructions

As a developer,
I want an LLM-optimized context file and executor instructions template,
So that AI agents working on my project understand HPNC concepts, and night-run agents follow strict rules.

**Acceptance Criteria:**

**Given** the MkDocs documentation from Story 6.1
**When** the HPNC.md generator is run
**Then** `scripts/generate_hpnc_md.py` reads MkDocs source files and produces a single `HPNC.md` (FR82)
**And** `HPNC.md` contains: system concepts, task status classes, CLI reference, frontmatter schema, and configuration summary
**And** `HPNC.md` is optimized for LLM consumption (concise, structured, no navigation artifacts)
**And** `HPNC.md` is regenerable via a single command: `python scripts/generate_hpnc_md.py` (NFR32)
**And** generated `HPNC.md` is placed in `_hpnc/HPNC.md` for the target project

**Given** executor instructions
**When** the full executor-instructions.md is created
**Then** `_hpnc/executor-instructions.md` extends the template from Story 3.2 with complete rules for autonomous night execution (FR83)
**And** instructions cover: commit convention (Conventional Commits), forbidden actions (no force-push, no protected path modification), testing requirements, scope boundaries
**And** instructions are project-specific and manually maintainable by the developer

**Given** documentation sync requirements
**Then** `HPNC.md` content stays in sync with MkDocs sources (NFR31)
**And** a CI check or pre-commit hook can verify HPNC.md is up-to-date
