---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
lastStep: 8
status: 'complete'
completedAt: '2026-04-06'
inputDocuments:
  - _bmad-output/planning-artifacts/prd.md
  - _bmad-output/hpnc-konzept-v2.md
  - _bmad-output/brainstorming/brainstorming-session-2026-04-06-001.md
  - _bmad-output/planning-artifacts/implementation-readiness-report-2026-04-06.md
workflowType: 'architecture'
project_name: 'hpnc'
user_name: 'Julian'
date: '2026-04-06'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

89 FRs across 11 capability areas, mapping to these architectural components:

| Architectural Component | FRs | Scope |
|------------------------|-----|-------|
| CLI Layer | FR1-FR8, FR27-FR31 | Entry point for all user interaction. 5 core commands (Phase 1), 10+ commands (Phase 2). Shell completion, project root discovery, exit codes. |
| Config Loader | FR5-FR7 | Project root discovery (upward search), YAML parsing, default merging, validation. Central dependency for all components. |
| Validation Engine | FR18-FR26 | Pre-flight checks against night-ready frontmatter schema. Pure read-only (NFR15). |
| Queue Manager | FR9-FR17 | Parses `night-queue.yaml`, resolves `depends_on` and `release_policy`. Exposes frontmatter schema (FR16). |
| Dispatcher | FR32-FR34 | Orchestrates sequential task execution. Persists state after every transition. Cleans up completed tasks. |
| Task-Runner | FR35-FR52 | State machine per task. Manages worktree lifecycle, invokes agents, runs gates, writes run artifacts. |
| AgentExecutor | FR69-FR75 | Interface with 3 capabilities (start, stream, exit-status). Mock executor ships built-in. Routing based on story frontmatter. |
| Quality Gates | FR53-FR58 | Build, tests, lint verification. Protected paths check (Phase 2). Auto-merge on policy (Phase 2). |
| Report Generator | FR59-FR68 | Morning report, task details, failure explanations with recommended next actions. |
| Logging | FR76-FR77 | Configurable dispatcher logging + agent output capture. |
| Human Review Workflow | FR85-FR89 | `proposal` status with approve/reject CLI commands. Review instructions in report. (Phase 2) |
| Documentation System | FR80-FR84 | MkDocs (de/en), CLI help, LLM context file (`HPNC.md`). |

**Non-Functional Requirements:**

32 NFRs driving architecture decisions:

| NFR Category | Key Architectural Impact |
|-------------|------------------------|
| Reliability (NFR1-6) | Every state transition must be persisted to disk. No silent failures. Agent crashes handled gracefully. |
| Data Integrity (NFR7-11) | Atomic writes for all persisted files. No false-positive gate passes. Files outside worktree untouched. |
| Recoverability (NFR12-13) | Startup recovery: detect orphaned worktrees, stale state, incomplete queue. Next `hpnc start` must work without cleanup. |
| Idempotency (NFR14-16) | Dispatcher lock to prevent double-start. Validate is read-only. Init is safe on existing projects. |
| Graceful Degradation (NFR17) | Refuse to start if any required agent unreachable. No degraded mode in Phase 1. |
| Performance (NFR21-23) | CLI < 2s, dispatcher overhead < 60s, state writes < 1s. Lazy imports for fast startup. |
| Error Messages (NFR24) | Every error: what happened + why + what to do. Cross-cutting concern for all components. |
| Cross-Platform (NFR28-30) | Windows 10/11 primary. `pathlib` everywhere. Handle long paths, file locking, case-insensitive FS. |

**Scale & Complexity:**

- Primary domain: CLI Tool / AI Agent Orchestration
- Complexity level: Medium-High
- Estimated architectural components: 12 (CLI, Config, Validation, Queue, Dispatcher, Task-Runner, State Machine, AgentExecutor, Gates, Reports, Logging, Workspace)
- Phase 1 scope: ~60 FRs, single-task sequential execution
- Phase 2 scope: +29 FRs, multi-task, fix-loop, human review

### Layered Architecture

Components follow a strict dependency hierarchy. Lower layers must not know about upper layers.

```
CLI Layer (Typer/Click + Rich)
  ├── Dispatcher
  │     └── Task-Runner
  │           ├── State Machine (core/state_machine.py)
  │           ├── AgentExecutor (interface + implementations)
  │           ├── Quality Gates
  │           └── TaskEventListener (interface)
  ├── Validation Engine
  ├── Queue Manager
  └── Report Generator

Shared Foundation (used by all layers):
  ├── Config Loader
  ├── Workspace (file I/O, atomic writes)
  └── Logging
```

**Dependency Rule:** Components may only depend downward or on Shared Foundation. AgentExecutor does not know about Dispatcher. Quality Gates do not know about Queue. This enables isolated testing of every component.

### Dispatcher ↔ Task-Runner Communication

**Phase 1 (sequential):** Dispatcher starts Task-Runner as subprocess, waits for exit. Exit code signals completion, `run.yaml` contains the result. Simple, robust.

**Architecture for extensibility:** Task-Runner uses a `TaskEventListener` interface for all status updates:

```python
class TaskEventListener(Protocol):
    def on_status_change(self, task: str, old: str, new: str): ...
    def on_progress(self, task: str, phase: str, detail: str): ...
    def on_complete(self, task: str, result: RunResult): ...
```

| Phase | Listener Implementation | Behavior |
|-------|------------------------|----------|
| 1 | `FileEventListener` | Writes status updates to `run.yaml` |
| 3 | `AsyncEventListener` | Notifies Dispatcher asynchronously for parallel execution |
| 4+ | `WebSocketEventListener` | Pushes real-time updates to Web-UI dashboard |

Task-Runner code stays identical across all phases — only the injected listener changes.

### Testability as Architectural Property

The 4-layer test strategy from the PRD requires these architectural patterns:

**Constructor Injection (no DI framework):**
Every component receives its dependencies as constructor parameters:
```python
TaskRunner(
    executor: AgentExecutor,
    gates: GateRunner,
    listener: TaskEventListener,
    workspace: Workspace,
    config: Config
)
```
This enables mock injection at every boundary.

**Workspace Object:**
A thin abstraction for all file operations:
- `read_yaml(path)`, `write_yaml_atomic(path, data)`, `read_markdown(path)`
- Encapsulates atomic writes (write-to-temp, rename)
- In tests: points to a temp directory
- In production: points to project root

**No Global Singletons:**
Dispatcher state and Task-Runner state are passed as parameters, not stored as global variables. This enables parallel test execution.

**State Machine as Independent Module:**
`hpnc/core/state_machine.py` — pure logic, no I/O, no dependencies on Task-Runner. Receives current state and event, returns new state. Fully unit-testable with zero dependencies.

### Technical Constraints & Dependencies

| Constraint | Source | Impact |
|-----------|--------|--------|
| Python 3.12+ | PRD Tech Stack | Language, ecosystem, distribution model |
| Typer/Click + Rich | PRD Tech Stack | CLI framework, output formatting |
| pip/pipx distribution | PRD Tech Stack | Package structure, entry points |
| Git subprocess (no gitpython) | PRD / Party Mode | Thin wrapper needed for all Git operations |
| Separate processes for Task-Runners | PRD Scoping | No threading; communication via TaskEventListener |
| YAML/JSON/Markdown artifacts | PRD / Concept Doc | All state is file-based, committed to Git. No SQLite. |
| Windows 10/11 primary | NFR28 | Path handling, file locking, process management |
| Claude Code + Codex CLI | FR2-FR3, FR69-FR75 | External subprocess dependencies |

### Cross-Cutting Concerns

| Concern | Affects | Architectural Pattern |
|---------|---------|----------------------|
| Atomic file writes | All state files | `Workspace.write_yaml_atomic()` — write-to-temp-then-rename |
| Project root discovery | All CLI commands | `ConfigLoader.find_root()` — upward search for `_hpnc/config.yaml` |
| Error message format | All components | Structured error class with `what`, `why`, `action` fields |
| Exit codes (0-5) | All CLI commands | Central exit code mapping in CLI layer |
| Logging | All components | Configurable verbosity, timestamped, injected logger |
| Windows path handling | All file operations | `pathlib` in all components, enforced via `Workspace` |
| Config loading | All components | `ConfigLoader` in Shared Foundation, injected via constructor |
| Dependency Injection | All components | Constructor injection, no framework, no globals |

## Starter Template Evaluation

### Primary Technology Domain

Python CLI Tool with AI Agent Orchestration — no web framework, no database, no frontend.

### Options Considered

| Option | Verdict |
|--------|---------|
| `uv init --package` | **Selected** — fast, standard-compliant, all-in-one |
| Poetry | Rejected — proprietary metadata format, slower, no Python version management |
| Hatch | Viable but no advantage over uv for this project |
| Cookiecutter Typer templates | Rejected — generic, partially outdated, HPNC needs specific structure |
| Manual setuptools + pip | Rejected — requires 5 separate tools (pip + venv + pyenv + build + twine), no lockfile |

### Selected Starter: uv

**Rationale:** uv is the 2026 standard for Python project management. It uses PEP 621 pyproject.toml (no vendor lock-in), handles everything from dependencies to builds to publishing, and is 10-100x faster than pip. For a solo developer starting a new CLI project, uv eliminates all packaging friction. Users still install HPNC with `pip install hpnc` or `pipx install hpnc` — uv is the development tool, not a user dependency.

**Initialization Command:**

```bash
uv init hpnc --package --python 3.12
cd hpnc
uv add typer "rich>=13" pyyaml
uv add --dev pytest pytest-cov ruff mypy
```

**Architectural Decisions Provided by Starter:**

- **Language & Runtime:** Python 3.12+, managed via `.python-version`
- **Package Format:** PEP 621 `pyproject.toml` with `[project.scripts]` entry point
- **Build Backend:** `uv_build` (fast, zero-config, integrated)
- **Dependency Locking:** `uv.lock` for reproducible builds
- **Virtual Environment:** Automatic, managed by uv
- **Distribution:** `uv build` → `uv publish` → pip/pipx installable

**Decisions NOT made by starter (addressed in architecture):**

- Project internal module structure (next step)
- CI/CD pipeline design
- Test configuration details

**Note:** Project initialization using `uv init` should be the first implementation story.

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
- Project module structure (decided)
- State machine pattern and states (decided)
- Error handling strategy (decided)
- Process management pattern (decided)

**Important Decisions (Shape Architecture):**
- Logging approach (decided)
- CLI structure (decided)
- Gate extensibility pattern (prepared, Phase 2 implementation)

**Deferred Decisions (Post-MVP):**
- Gate-Registry implementation (Phase 2, interface prepared)
- `gates_required` frontmatter field (Phase 2 implementation, Phase 1 schema inclusion)
- Web interface layer (Phase 3+)
- Screenshot/visual verification in reports (TBD)

### Project Module Structure

```
src/hpnc/
├── cli/                    # CLI Layer (Typer)
│   ├── app.py              # Typer App + Subcommand registration
│   ├── init_cmd.py
│   ├── validate_cmd.py
│   ├── start_cmd.py
│   ├── status_cmd.py
│   └── queue_cmd.py
├── core/                   # Business Logic (framework-independent)
│   ├── state_machine.py    # Pure State Machine (no I/O)
│   ├── dispatcher.py       # Orchestration
│   ├── task_runner.py      # Task Lifecycle
│   ├── validator.py        # Frontmatter Validation
│   └── queue_manager.py    # Queue Parsing + Logic
├── agents/                 # AgentExecutor Abstraction
│   ├── base.py             # AgentExecutor Protocol
│   ├── claude_code.py      # Claude Code Implementation
│   ├── codex.py            # Codex Implementation
│   └── mock.py             # Mock for tests + --mock
├── gates/                  # Quality Gates
│   ├── runner.py           # Gate orchestration (prepared for Registry pattern)
│   ├── build.py
│   ├── tests.py
│   └── lint.py
├── reporting/              # Report Generation
│   └── generator.py
├── infra/                  # Shared Foundation
│   ├── config.py           # Config Loader
│   ├── workspace.py        # File I/O + Atomic Writes
│   ├── git.py              # Git Subprocess Wrapper
│   ├── logging.py          # Logging Setup
│   └── errors.py           # Error Classes
└── schemas/                # Night-Ready Schema
    └── frontmatter.py      # Schema Definition + Validation
```

**Layering Rule:** `cli/` → `core/` → `agents/` + `gates/`, all use `infra/`. Lower layers never import from upper layers. `core/` is interface-agnostic — a future `web/` or `api/` layer would use the same `core/`.

### State Machine

**Pattern:** Enum + Transition Table — explicit, testable, easy to extend.

**Complete State Enum (all phases defined upfront):**

```python
class TaskState(Enum):
    # Phase 1 States
    QUEUED = "queued"
    SETUP_WORKTREE = "setup_worktree"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    GATES = "gates"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"

    # Phase 2 States (defined now, transitions added later)
    FIX_ATTEMPT = "fix_attempt"
    PAUSED = "paused"
    AWAITING_REVIEW = "awaiting_review"
    PROPOSAL = "proposal"
    MERGED = "merged"
    INTERRUPTED = "interrupted"
```

**Phase 1 Transition Table:**

```python
TRANSITIONS = {
    TaskState.QUEUED: [TaskState.SETUP_WORKTREE],
    TaskState.SETUP_WORKTREE: [TaskState.IMPLEMENTATION, TaskState.FAILED],
    TaskState.IMPLEMENTATION: [TaskState.REVIEW, TaskState.BLOCKED],
    TaskState.REVIEW: [TaskState.GATES, TaskState.BLOCKED],
    TaskState.GATES: [TaskState.DONE, TaskState.FAILED],
}
```

States are generic workflow phases, not task types. The differentiation between code/UI/DB/API tasks happens at the gate level, not the state level.

### Gate Extensibility

**Phase 1:** Hardcoded gates — build + tests + lint. Gate runner executes all three sequentially.

**Phase 2 preparation:** `gates_required` as a frontmatter field in the night-ready schema. This field serves a dual purpose:

1. **Pre-run validation** (`hpnc validate`): Checks whether the infrastructure for all required gates is available. A UI task requiring `storybook` with no Storybook installed → validate fails.
2. **Post-implementation execution** (Task-Runner): Runs exactly the gates specified, not more.

Phase 1 `hpnc validate` checks `gates_required` against a whitelist of known gates (build, tests, lint). Unknown gate names produce a warning. This ensures the field is validated from day one even before the Gate-Registry exists.

**Phase 2 Gate-Registry:**

```python
class GateRegistry:
    def register(self, name: str, gate: Gate): ...
    def run(self, required: list[str]) -> GateResults: ...
    def check_available(self, required: list[str]) -> list[str]: ...  # For validate
```

Enables task-specific gates:
- UI tasks: + storybook, a11y, playwright
- DB tasks: + migration_check
- API tasks: + api_spec_check

No state machine changes needed — only new gate implementations registered.

### Error Handling

```python
class HpncError(Exception):
    """Base error with what/why/action (NFR24)."""
    def __init__(self, what: str, why: str, action: str): ...

class ConfigError(HpncError): ...           # Exit Code 4
class ConnectivityError(HpncError): ...      # Exit Code 5
class ValidationError(HpncError): ...        # Exit Code 1
class TaskBlockedError(HpncError): ...       # Exit Code 2
class TaskInterruptedError(HpncError): ...   # Exit Code 3
```

CLI catches `HpncError` and formats output with Rich. Every error carries the three fields NFR24 requires (what happened, why, what to do).

### Logging

stdlib `logging` with Rich handler for terminal output. `logging.FileHandler` for dispatcher log files.

- Terminal: Rich-formatted, colored, human-readable
- File: Plain text with timestamps, written to `_hpnc/runs/` per night run
- Verbosity: configurable via `config.yaml` (minimal / normal / verbose)
- No additional dependencies (Rich already required for CLI output)

### CLI Structure

```python
app = typer.Typer()
queue_app = typer.Typer()
app.add_typer(queue_app, name="queue")

@app.command()
def init(): ...
@app.command()
def validate(): ...
@app.command()
def start(at: str = None, delay: str = None, dry_run: bool = False, mock: bool = False): ...
@app.command()
def status(): ...
@queue_app.command()
def add(story: Path): ...
```

`queue` as sub-app, rest as top-level commands. Matches PRD command tree.

### Process Management

**Dispatcher → Task-Runner Interface:**

The Dispatcher writes a `task-spec.yaml` for each task, then starts the Task-Runner with a single argument pointing to this file:

```yaml
# Generated by Dispatcher, one per task
story: stories/login-validation.md
worktree: /tmp/hpnc-night/login-validation
executor: opus
reviewer: codex
config: _hpnc/config.yaml
instructions: _hpnc/executor-instructions.md
run_dir: _hpnc/runs/2026/04/06/001_login-validation
```

```python
result = subprocess.run(
    [sys.executable, "-m", "hpnc.core.task_runner", str(task_spec_path)],
    capture_output=True
)
```

Clean handoff: all context serialized, debuggable, no implicit state. Task-Runner reads the spec and has everything it needs.

Task-Runner is independently executable (`python -m hpnc.core.task_runner`). This enables:
- Phase 1: synchronous `subprocess.run()`
- Phase 3: asynchronous `asyncio.create_subprocess_exec()`
- No architectural change needed for parallelization

Task-Runner communicates status via `TaskEventListener` interface:

```python
class TaskEventListener(Protocol):
    def on_status_change(self, task: str, old: str, new: str): ...
    def on_progress(self, task: str, phase: str, detail: str): ...
    def on_complete(self, task: str, result: RunResult): ...
```

Phase 1: `FileEventListener` writes to `run.yaml`. Future: `AsyncEventListener` for parallel dispatch, `WebSocketEventListener` for web UI.

### Scheduling (`--at` / `--delay`)

**Phase 1 Decision:** `time.sleep()` with sleep/hibernate guard.

When `hpnc start --at 23:00` is called, the process calculates the delay and sleeps. On wake, it checks if the target time has passed (handles sleep/hibernate time jumps). If the target time is in the past, it starts immediately.

Rationale: Simple, no OS-specific code, no external scheduler dependency. The HPNC process stays alive but idle. Acceptable for Phase 1 where the developer starts it before bed.

Phase 3+: Could optionally register with OS scheduler (Task Scheduler / cron) for more robust scheduling.

### Decision Impact Analysis

**Implementation Waves (recommended sequence for Epic creation):**

| Wave | Modules | What It Enables | Token Cost |
|------|---------|----------------|------------|
| 1 | Walking Skeleton + `infra/` + `schemas/` | Foundation, all interfaces as stubs | Zero |
| 2 | `core/state_machine.py` + `agents/mock.py` | Testable core logic without real agents | Zero |
| 3 | `gates/` + `core/task_runner.py` | Single task runs locally with mock | Zero |
| 4 | `core/dispatcher.py` + `core/validator.py` + `core/queue_manager.py` | Full night run with mock agents | Zero |
| 5 | `reporting/` + `cli/` | HPNC usable end-to-end with `--mock` | Zero |
| 6 | `agents/claude_code.py` + `agents/codex.py` | Real agent integration | Tokens needed |

**Key insight:** Waves 1-5 are completely token-free. 80% of development requires zero API calls. Wave 6 flips the switch to real agents. This naturally validates the Mock-first test strategy.

**Implementation Sequence (module level):**
1. `infra/` (Config, Workspace, Git, ProcessLock, Errors, Logging)
2. `schemas/` (Frontmatter schema incl. `gates_required`)
3. `core/state_machine.py` — pure logic, testable immediately
4. `agents/base.py` + `agents/mock.py` — enables token-free development
5. `gates/` — build, tests, lint
6. `events/` — TaskEventListener Protocol + FileEventListener
7. `core/task_runner.py` — combines state machine + agents + gates + event listener
8. `core/dispatcher.py` — orchestrates task runners
9. `core/validator.py` + `core/queue_manager.py`
10. `reporting/generator.py`
11. `cli/` — thin layer connecting user to core
12. `agents/claude_code.py` + `agents/codex.py` — real agent integration

**Cross-Component Dependencies:**

```
cli/* → core/* → agents/base.py (Protocol)
                → gates/runner.py
                → infra/*
                → schemas/*
agents/claude_code.py → infra/workspace.py, infra/errors.py
agents/mock.py → infra/workspace.py
gates/* → infra/workspace.py, infra/errors.py
reporting/* → infra/workspace.py
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
hpnc/                               # Repository root
├── pyproject.toml                   # Package config, deps, entry points, ruff/mypy config
├── uv.lock                          # Dependency lockfile (auto-generated)
├── .python-version                  # Python 3.12
├── README.md                        # Quick start guide
├── LICENSE                          # MIT
├── .gitignore
├── .pre-commit-config.yaml          # Pre-commit hooks (ruff, mypy)
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Lint + type check + unit + integration tests
│       └── release.yml              # Build + publish to PyPI
├── docs/                            # MkDocs documentation source
│   ├── mkdocs.yml                   # MkDocs config (Material theme + i18n)
│   ├── de/
│   │   ├── index.md
│   │   ├── getting-started.md
│   │   ├── concepts/
│   │   │   ├── night-policy.md
│   │   │   ├── story-format.md
│   │   │   ├── two-layer-release.md
│   │   │   └── state-machine.md
│   │   ├── cli/
│   │   │   ├── init.md
│   │   │   ├── validate.md
│   │   │   ├── start.md
│   │   │   ├── status.md
│   │   │   └── queue.md
│   │   ├── configuration/
│   │   │   ├── config-yaml.md
│   │   │   ├── frontmatter-schema.md
│   │   │   └── known-resources.md
│   │   └── troubleshooting.md
│   └── en/
│       └── ...                      # Same structure, English
├── scripts/
│   └── generate_hpnc_md.py         # Generates HPNC.md from MkDocs sources
├── src/
│   └── hpnc/                        # src layout for import safety (PEP 517)
│       ├── __init__.py              # Package version, __all__
│       ├── __main__.py              # Entry point for `python -m hpnc`
│       ├── py.typed                 # PEP 561 typed package marker
│       ├── constants.py             # Global constants
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── app.py               # Typer App + subcommand registration
│       │   ├── init_cmd.py
│       │   ├── validate_cmd.py
│       │   ├── start_cmd.py
│       │   ├── status_cmd.py
│       │   └── queue_cmd.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── __main__.py          # Entry point for `python -m hpnc.core.task_runner`
│       │   ├── state_machine.py     # TaskState enum, transition table, pure logic
│       │   ├── dispatcher.py        # Queue processing, task-runner orchestration
│       │   ├── task_runner.py       # Task lifecycle
│       │   ├── validator.py         # Frontmatter + infrastructure validation
│       │   └── queue_manager.py     # night-queue.yaml parsing
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py              # AgentExecutor Protocol
│       │   ├── claude_code.py       # Claude Code CLI executor
│       │   ├── codex.py             # Codex CLI executor
│       │   └── mock.py              # Configurable mock executor
│       ├── gates/
│       │   ├── __init__.py
│       │   ├── runner.py            # Gate orchestration (prepared for Registry)
│       │   ├── build.py
│       │   ├── tests.py
│       │   └── lint.py
│       ├── reporting/
│       │   ├── __init__.py
│       │   └── generator.py         # Markdown report generation
│       ├── events/
│       │   ├── __init__.py
│       │   ├── base.py              # TaskEventListener Protocol
│       │   └── file_listener.py     # Phase 1: writes status to run.yaml
│       ├── infra/
│       │   ├── __init__.py
│       │   ├── config.py            # ConfigLoader, project root discovery
│       │   ├── workspace.py         # File I/O, atomic writes
│       │   ├── git.py               # Git subprocess wrapper
│       │   ├── process_lock.py      # Dispatcher lock (NFR14, cross-platform)
│       │   ├── logging.py           # Logging setup
│       │   └── errors.py            # HpncError hierarchy
│       └── schemas/
│           ├── __init__.py
│           └── frontmatter.py       # Night-ready schema + validation
└── tests/
    ├── conftest.py                  # Global fixtures (tmp_workspace, mock_executor)
    ├── fixtures/
    │   ├── stories/
    │   │   ├── valid_night_ready.md
    │   │   ├── missing_tests_required.md
    │   │   ├── empty_blocking_questions.md
    │   │   └── ui_task_with_gates.md
    │   ├── configs/
    │   │   ├── default_config.yaml
    │   │   └── minimal_config.yaml
    │   ├── queues/
    │   │   ├── single_task.yaml
    │   │   └── with_dependencies.yaml
    │   └── runs/
    │       ├── successful_run.yaml
    │       └── failed_run.yaml
    ├── unit/
    │   ├── conftest.py              # Unit-specific fixtures
    │   ├── core/
    │   │   ├── test_state_machine.py
    │   │   ├── test_dispatcher.py
    │   │   ├── test_validator.py
    │   │   └── test_queue_manager.py
    │   ├── agents/
    │   │   └── test_mock.py
    │   ├── gates/
    │   │   └── test_runner.py
    │   ├── reporting/
    │   │   └── test_generator.py
    │   ├── schemas/
    │   │   └── test_frontmatter.py
    │   └── infra/
    │       ├── test_config.py
    │       ├── test_workspace.py
    │       ├── test_git.py
    │       └── test_errors.py
    ├── integration/
    │   ├── conftest.py              # Integration-specific fixtures (MockExecutor)
    │   ├── test_task_lifecycle.py
    │   ├── test_dispatcher_flow.py
    │   └── test_validate_flow.py
    ├── recordings/                  # Record/Replay data (Layer 3, Phase 2)
    │   ├── claude_code/
    │   │   ├── success_response.json
    │   │   └── timeout_response.json
    │   └── codex/
    │       └── review_response.json
    └── e2e/
        └── test_smoke.py
```

**Why `src/hpnc/` (src layout):** Not for multi-package support — for import safety. Without `src/`, running Python from the repo root imports the local source instead of the installed package. Tests would pass locally but fail after `pip install`. The src layout guarantees tests always run against the installed package.

### Architectural Boundaries

**Layer Boundaries (strict import rules):**

```
cli/  →  core/  →  agents/base.py (Protocol only)
                →  gates/runner.py
                →  events/base.py (Protocol only)
                →  schemas/
                →  infra/

agents/claude_code.py  →  infra/ only
agents/mock.py         →  infra/ only
gates/*                →  infra/ only
reporting/*            →  infra/ only
events/file_listener.py → infra/ only
```

**Forbidden imports:**
- `core/` must never import from `cli/`
- `agents/` must never import from `core/` or `cli/`
- `gates/` must never import from `core/` or `cli/`
- `infra/` must never import from any other `hpnc` module

**External Integration Boundaries:**
- Claude Code CLI: accessed only through `agents/claude_code.py`
- Codex CLI: accessed only through `agents/codex.py`
- Git: accessed only through `infra/git.py`
- Filesystem state: accessed only through `infra/workspace.py`
- Dispatcher lock: accessed only through `infra/process_lock.py`
- API keys/secrets: HPNC stores no credentials. Agent authentication is managed by their respective CLIs.

### Requirements to Structure Mapping

| FR Category | Primary Location | Supporting Files |
|------------|-----------------|-----------------|
| Project Setup (FR1-FR8) | `cli/init_cmd.py`, `infra/config.py` | `schemas/frontmatter.py` |
| Queue Management (FR9-FR17) | `core/queue_manager.py`, `cli/queue_cmd.py` | `schemas/frontmatter.py` |
| Validation (FR18-FR26) | `core/validator.py`, `cli/validate_cmd.py` | `schemas/frontmatter.py`, `infra/git.py` |
| Night Run (FR27-FR34) | `core/dispatcher.py`, `cli/start_cmd.py` | `infra/process_lock.py`, `infra/workspace.py` |
| Task Lifecycle (FR35-FR52) | `core/task_runner.py`, `core/state_machine.py` | `events/`, `infra/git.py`, `infra/workspace.py` |
| Quality Gates (FR53-FR58) | `gates/` | `infra/workspace.py` |
| Reporting (FR59-FR68) | `reporting/generator.py`, `cli/status_cmd.py` | `infra/workspace.py` |
| Agent Orchestration (FR69-FR75) | `agents/` | `infra/workspace.py`, `infra/errors.py` |
| Logging (FR76-FR77) | `infra/logging.py` | Used by all modules |
| BMAD Integration (FR78-FR79) | `schemas/frontmatter.py` | External: BMad Builder |
| Documentation (FR80-FR84) | `docs/`, `scripts/generate_hpnc_md.py` | `cli/` (--help auto-gen) |
| Human Review (FR85-FR89) | `cli/` (Phase 2), `reporting/` | `core/state_machine.py` |

### Data Flow

```
Story File (.md)
  → Queue Manager (parse frontmatter)
  → Validator (check night-ready + gates availability)
  → Dispatcher (acquire lock, orchestrate)
  → Task-Runner:
      → Git (create worktree + branch)
      → AgentExecutor (implement)
      → AgentExecutor (review)
      → Gate Runner (build, tests, lint)
      → Event Listener (write run.yaml at each transition)
  → Report Generator (compile results)
  → CLI (display to user)
```

### Runtime Project Files (created by `hpnc init`)

```
user-project/
├── _hpnc/
│   ├── config.yaml              # HPNC project config
│   ├── executor-instructions.md # Agent rules for this project
│   ├── known-resources.yaml     # Abstract resources for touches
│   ├── night-queue.yaml         # Current night queue
│   ├── dispatcher-state.yaml    # Runtime state
│   ├── .dispatcher.lock         # Process lock (NFR14)
│   ├── HPNC.md                  # LLM context file (generated)
│   ├── runs/
│   │   └── 2026/04/06/
│   │       └── 001_login-validation/
│   │           ├── run.yaml
│   │           ├── cost.json        # Phase 2
│   │           ├── review.md        # Phase 2
│   │           └── dispatcher.log
│   └── reports/
│       └── 2026/04/06/
│           └── 001-report.md
```

### Walking Skeleton (First Implementation Story)

The first story creates the complete directory structure with all interfaces as stubs:

**Story 1: "Project Bootstrap + Walking Skeleton"**
- `uv init` executed, `pyproject.toml` configured with all dependencies
- Complete directory structure created (all folders + `__init__.py` + `__all__`)
- All Protocol interfaces defined as stubs (`AgentExecutor`, `TaskEventListener`, `Gate`)
- `TaskState` Enum with all states (Phase 1 + Phase 2 labels)
- Phase 1 transition table implemented
- `MockAgentExecutor` as first concrete implementation
- `py.typed` marker present
- `__main__.py` in `hpnc/` and `hpnc/core/`
- `ruff` + `mypy` configured in `pyproject.toml`
- Pre-commit hooks configured
- First test: `test_state_machine_queued_to_setup_worktree_succeeds`
- CI pipeline (`.github/workflows/ci.yml`) runs green
- `hpnc --help` shows Typer-generated help

After this story, every subsequent story fills a module without structural conflicts. This is the ideal first task — clear, testable, no open questions.

### Test Fixtures Architecture

```python
# tests/conftest.py (global)
@pytest.fixture
def tmp_workspace(tmp_path):
    """Create a temporary HPNC workspace for testing."""
    config = tmp_path / "_hpnc" / "config.yaml"
    config.parent.mkdir(parents=True)
    config.write_text("project_name: test\n")
    return Workspace(root=tmp_path)

@pytest.fixture
def mock_executor():
    """Pre-configured mock agent executor."""
    return MockAgentExecutor(default_status=ExitStatus.SUCCESS, delay=0)
```

Global fixtures provide `tmp_workspace` and `mock_executor`. Sub-conftest files in `unit/` and `integration/` add layer-specific fixtures.

## Implementation Patterns & Consistency Rules

### Naming Patterns

**Python Code (PEP 8 — non-negotiable):**
- Functions/methods: `snake_case` — `load_config()`, `run_gates()`
- Classes: `PascalCase` — `TaskRunner`, `AgentExecutor`, `GateRegistry`
- Constants: `UPPER_SNAKE` — `MAX_FIX_ATTEMPTS`, `DEFAULT_TIMEOUT`
- Private: `_leading_underscore` — `_parse_frontmatter()`
- Modules/files: `snake_case` — `task_runner.py`, `state_machine.py`

**YAML Keys (config, state, frontmatter):**
- Always `snake_case`: `night_ready`, `merge_target`, `tests_required`
- Never camelCase in YAML

**Git Branches:**
- Night-run branches: `night/<task-name>` — e.g., `night/login-validation`
- Task names: lowercase, hyphens, no spaces — derived from story filename

**CLI Commands/Flags:**
- Commands: lowercase — `hpnc start`, `hpnc validate`
- Subcommands: lowercase — `hpnc queue add`
- Flags: `--kebab-case` — `--dry-run`, `--at`, `--mock`

### Code Conventions

**Docstrings — Google-Style (mandatory):**

```python
def validate_story(path: Path, schema: FrontmatterSchema) -> ValidationResult:
    """Validate a story file against the night-ready schema.

    Args:
        path: Path to the story markdown file.
        schema: The frontmatter schema to validate against.

    Returns:
        ValidationResult with status and any errors found.

    Raises:
        ValidationError: If the file cannot be parsed.
    """
```

Google-Style is concise, readable, and supported by `mkdocstrings` for MkDocs documentation generation.

**Interfaces — Protocol (structural typing, no ABC):**

```python
from typing import Protocol

class AgentExecutor(Protocol):
    def start(self, story: Path, config: Config, instructions: Path) -> Process: ...
    def stream_output(self, process: Process) -> Iterator[str]: ...
    def get_exit_status(self, process: Process) -> ExitStatus: ...
```

Protocol over ABC: no inheritance required, mocks only need to implement the methods, not extend a base class.

**Return Patterns — Core returns Results, CLI throws Exceptions:**

```python
# Core — returns result, never throws for expected cases
def run_gates(worktree: Path, required: list[str]) -> GateResults:
    ...

# CLI — converts results to exceptions for exit codes
if not result.passed:
    raise ValidationError(what=..., why=..., action=...)
```

This keeps `core/` free from exit-code logic and independently testable.

**Public API — `__all__` in every `__init__.py`:**

```python
# hpnc/core/__init__.py
__all__ = ["Dispatcher", "TaskRunner", "TaskState", "ValidationResult"]
```

Defines which names are part of the stable interface. Prevents agents from importing internal helpers that may change.

**No Magic Strings — use Enums and Constants:**

```python
# Bad
if status == "done":

# Good
if status == TaskState.DONE:
```

All status values, gate names, config keys as Enum or constant. Never string literals scattered in code.

**Three Levels of Configurable Values:**

| Level | Where | Example | Changeable? |
|-------|-------|---------|-------------|
| Constant | Code (`constants.py` per module) | `MAX_TASK_NAME_LENGTH = 50` | Only by code change |
| Default | Code, overridable | `timeout: 30m` | In config.yaml |
| Config | `config.yaml` | `merge_target: develop` | By user |

Rule: anything the user might ever want to change → Config with default in code. Implementation details → Constant.

**Type Annotations:**
- All public functions: fully typed parameters and return types
- Protocol classes for interfaces (`AgentExecutor`, `TaskEventListener`, `Gate`)
- `mypy --strict` as target (enforced in CI)
- Use `pathlib.Path` for all paths, never `str` for file paths

**TODO Convention:**

```python
# TODO(phase-2): Add fix-loop support
# TODO(phase-3): Replace with async subprocess
# FIXME: Workaround for Windows long path issue — see issue #42
```

Always with phase tag or justification. Bare `# TODO` without context is forbidden.

### Structure Patterns

**Test Organization:**

```
tests/
├── fixtures/               # Shared test data
│   ├── stories/
│   │   ├── valid_night_ready.md
│   │   ├── missing_tests_required.md
│   │   └── empty_blocking_questions.md
│   ├── configs/
│   │   ├── default_config.yaml
│   │   └── minimal_config.yaml
│   └── runs/
│       ├── successful_run.yaml
│       └── failed_run.yaml
├── unit/                   # Mirrors src/hpnc/ structure
│   ├── core/
│   │   ├── test_state_machine.py
│   │   ├── test_dispatcher.py
│   │   └── test_validator.py
│   ├── agents/
│   │   └── test_mock.py
│   └── infra/
│       ├── test_config.py
│       └── test_workspace.py
├── integration/            # Mock-AgentExecutor tests
│   ├── test_task_lifecycle.py
│   └── test_dispatcher_flow.py
└── e2e/                    # Real agent tests (expensive, rare)
    └── test_smoke.py
```

**Test Naming Convention:**

```python
# Pattern: test_<what>_<when>_<expected>
def test_state_machine_queued_to_setup_worktree_succeeds(): ...
def test_state_machine_invalid_transition_raises(): ...
def test_validator_missing_night_ready_returns_error(): ...
```

Test name must describe what is broken when the test fails.

**Import Order (enforced by ruff):**
1. stdlib (`pathlib`, `subprocess`, `logging`)
2. third-party (`typer`, `rich`, `yaml`)
3. local (`hpnc.core`, `hpnc.infra`)

### Format Patterns

**YAML Files (all HPNC artifacts):**
- Indentation: 2 spaces
- Strings: unquoted unless containing special characters
- Lists: dash-space format (`- item`)
- Booleans: `true`/`false` (lowercase)
- Null: explicit `null`, never empty value
- Dates: ISO 8601 (`2026-04-06T23:00:00`)

**run.yaml canonical format:**

```yaml
status: done
executor: opus
reviewer: codex
branch: night/login-validation
started: 2026-04-06T23:12:00
finished: 2026-04-06T23:36:00
files_changed:
  - src/components/LoginForm.tsx
  - src/components/LoginForm.test.tsx
story_source: stories/login-validation.md
```

**Markdown Reports:**
- Tables use pipe format with header separator
- Status uses plain text — no emojis in machine-readable files
- Recommended actions prefixed with `→`

### Commit Convention

**Conventional Commits (mandatory for all agents):**

```
<type>(<scope>): <description>

feat(login): add inline validation error messages
fix(gates): handle missing test command gracefully
test(state-machine): add transition edge case tests
refactor(dispatcher): extract queue cleanup into separate method
docs(readme): add installation instructions
chore(deps): update typer to 0.15
```

Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`
Scope: module or feature name

This convention is included in `executor-instructions.md` so night-run agents follow it. Enables automatic changelogs and makes morning `git log` review meaningful.

### Logging Convention

| Level | When to Use | Example |
|-------|------------|---------|
| `DEBUG` | Detailed flow info, only at verbose | `"Parsing frontmatter from story.md"` |
| `INFO` | Significant workflow events | `"Task login-validation: QUEUED → IMPLEMENTATION"` |
| `WARNING` | Unexpected but handled behavior | `"Unknown gate 'storybook' in gates_required, skipping"` |
| `ERROR` | Failures affecting task or run | `"Gate 'tests' failed: exit code 1"` |
| `CRITICAL` | System-level, dispatcher cannot continue | `"Dispatcher state file corrupt, aborting"` |

Rule: `INFO` events alone must tell the complete story of a night run. `DEBUG` adds detail. `WARNING`+ signals problems.

### Process Patterns

**Error Handling:**
- All errors are `HpncError` subclasses with `what`/`why`/`action`
- CLI catches `HpncError` at top level, formats with Rich
- Unexpected exceptions → log full traceback + generic error message
- Never `except Exception: pass` — silent swallowing is a critical bug (NFR1)

**Atomic File Operations:**
- All state writes use `Workspace.write_yaml_atomic()`
- Never write directly to state files
- Read operations don't need atomicity

**Subprocess Calls (Git, Agents):**
- Always `subprocess.run()` with `capture_output=True`
- Always check `returncode`
- Always `str(path)` for cross-platform path conversion
- Never `shell=True`

**No `print()` statements** — all output through Rich console or logging

### Enforcement

**Tooling:**
- `ruff` for linting and formatting (replaces flake8, black, isort)
- `mypy --strict` for type checking
- Pre-commit hooks for automated enforcement

**All AI Agents MUST:**
- Follow PEP 8 and all naming conventions without exception
- Use `Workspace` for all file I/O — never raw `open()` on state files
- Use `HpncError` subclasses — never bare `raise Exception`
- Use `subprocess.run()` with `capture_output=True` — never `os.system()`
- Add type annotations to all public functions
- Write Google-Style docstrings on all public functions
- Use Conventional Commits for all commit messages
- Write tests in the matching `tests/` location with descriptive names

## Architecture Validation Results

### Coherence Validation

**Decision Compatibility:** All technology choices work together without conflicts. Python 3.12+ with Typer + Rich + PyYAML + uv — standard ecosystem, no version conflicts. subprocess-based Git and Agent execution avoids library-level dependencies.

**Pattern Consistency:** PEP 8 naming + Google docstrings + Protocol interfaces + Constructor Injection — all standard Python patterns, no contradictions. Atomic writes via Workspace + state persistence via EventListener — consistent file-safety approach. HpncError hierarchy + exit codes + Rich formatting — unified error pipeline.

**Structure Alignment:** Layered architecture (cli → core → agents/gates/events → infra) with strict import rules. Every FR category maps to exactly one primary module. Walking Skeleton ensures structure exists before modules are filled.

### Requirements Coverage

**Functional Requirements: 89/89 covered (100%)**

All FR categories have explicit architectural homes with primary and supporting modules mapped in the FR-to-Structure Mapping table.

**Non-Functional Requirements: 32/32 covered (100%)**

All NFR categories addressed by architectural patterns:
- Reliability → EventListener at every transition, state persistence
- Data Integrity → Workspace atomic writes, strict gate checking
- Recoverability → Dispatcher startup recovery
- Idempotency → ProcessLock (testable: unit test verifies double-lock exception)
- Performance → Lazy imports, minimal overhead
- Error Messages → HpncError(what, why, action)
- Cross-Platform → pathlib, Workspace abstraction

### Implementation Readiness

**Decision Completeness:** All critical decisions documented with technology choices, versions, rationale, and code examples. Scheduling mechanism decided (time.sleep + hibernate guard). Dispatcher→Task-Runner interface specified (task-spec.yaml).

**Structure Completeness:** Full project tree with every file specified. No generic placeholders. FR mapping, data flow, runtime files, and test fixtures all defined.

**Pattern Completeness:** Naming, structure, format, process, commit, logging, error handling, type annotation, TODO, and docstring conventions all defined with examples and enforcement tooling.

### Gap Analysis

**Critical Gaps: None**

**Important Gaps (address during implementation):**

| Gap | Recommendation |
|-----|---------------|
| CI pipeline details | Define in Walking Skeleton story: ruff + mypy + pytest unit + integration, cache uv deps |
| MkDocs i18n plugin | Use `mkdocs-static-i18n`, decide during docs story |
| ReplayAgentExecutor for Layer 3 testing | `tests/recordings/` directory structure prepared, implement in Phase 2 |

### Architecture Completeness Checklist

- [x] Project context analyzed (89 FRs, 32 NFRs, 5 journeys)
- [x] Technology stack specified (Python 3.12+, Typer, Rich, uv)
- [x] State machine defined (14 states, Phase 1 transitions, Phase 2 labels)
- [x] AgentExecutor Protocol (3 capabilities, Mock built-in)
- [x] TaskEventListener Protocol (extensible for WebSocket)
- [x] Dispatcher→Task-Runner interface (task-spec.yaml)
- [x] Scheduling mechanism (time.sleep + hibernate guard)
- [x] Error hierarchy (HpncError with what/why/action)
- [x] Gate extensibility prepared (gates_required, Registry pattern)
- [x] Process management (subprocess, async-ready)
- [x] Complete directory structure with all files
- [x] Architectural boundaries and forbidden imports
- [x] FR-to-structure mapping (100% coverage)
- [x] Implementation Waves for Epic guidance
- [x] Walking Skeleton story fully specified
- [x] All naming, coding, testing, commit conventions defined
- [x] Enforcement tooling specified (ruff, mypy, pre-commit)

### Architecture Readiness Assessment

**Overall Status: READY FOR IMPLEMENTATION**

**Confidence Level: High**

**Key Strengths:**
- 100% FR and NFR coverage with explicit architectural support
- Clean layered architecture enabling future web/API interfaces without rewrites
- Testability baked in (Protocols, Constructor Injection, MockExecutor, Workspace)
- Implementation Waves 1-5 are token-free — 80% development without API costs
- Walking Skeleton enables parallel development from Story 2
- Phase 2-4 extensibility prepared without overengineering

**First Implementation Priority:**
```bash
uv init hpnc --package --python 3.12
```
Execute Walking Skeleton Story 1, then follow Implementation Waves sequentially.
