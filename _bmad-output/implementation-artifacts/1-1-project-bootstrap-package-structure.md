# Story 1.1: Project Bootstrap & Package Structure

Status: done

## Story

As a developer,
I want to initialize the HPNC project with uv as a properly structured Python package,
so that the project is installable, `hpnc --help` works, and all development tooling is configured.

## Acceptance Criteria

1. `pyproject.toml` exists with project metadata, all dependencies (typer, rich, pyyaml), and dev dependencies (pytest, pytest-cov, ruff, mypy)
2. Complete `src/hpnc/` directory structure exists with all subdirectories (`cli/`, `core/`, `agents/`, `gates/`, `reporting/`, `events/`, `infra/`, `schemas/`)
3. Every `__init__.py` contains an `__all__` export list
4. `src/hpnc/__main__.py` and `src/hpnc/core/__main__.py` exist as entry points
5. `src/hpnc/py.typed` marker exists (PEP 561)
6. `ruff` and `mypy` are configured in `pyproject.toml`
7. `.pre-commit-config.yaml` is configured with ruff and mypy hooks
8. `.gitignore` covers Python, uv, and IDE artifacts
9. `LICENSE` exists with MIT license
10. `hpnc --help` displays Typer-generated help showing all command stubs (init, validate, start, status, queue)
11. Shell completion is available for bash, zsh, and fish via Typer (FR8)
12. `ruff check` and `mypy --strict` pass with zero errors
13. `tests/` directory structure mirrors `src/hpnc/` with `conftest.py` files

## Tasks / Subtasks

- [x] Task 1: Initialize project with uv (AC: 1)
  - [x] Run `uv init hpnc --package --python 3.12`
  - [x] Add runtime dependencies: `uv add typer "rich>=13" pyyaml`
  - [x] Add dev dependencies: `uv add --dev pytest pytest-cov ruff mypy`
  - [x] Configure `[project.scripts]` entry point: `hpnc = "hpnc.cli.app:main"`
  - [x] Set project metadata: name, version 0.1.0, description, MIT license, requires-python >=3.12
- [x] Task 2: Create complete source directory structure (AC: 2, 3, 4, 5)
  - [x] Create all package directories under `src/hpnc/`: cli, core, agents, gates, reporting, events, infra, schemas
  - [x] Create `__init__.py` with `__all__` in every package (see File Structure below for exact exports)
  - [x] Create `src/hpnc/__main__.py` (entry point for `python -m hpnc`)
  - [x] Create `src/hpnc/core/__main__.py` (entry point for `python -m hpnc.core.task_runner`)
  - [x] Create `src/hpnc/py.typed` (empty file, PEP 561 marker)
  - [x] Create `src/hpnc/constants.py` for global constants
- [x] Task 3: Implement CLI skeleton with Typer (AC: 10, 11)
  - [x] Create `src/hpnc/cli/app.py` with Typer app and all command stubs
  - [x] Create stub command files: init_cmd.py, validate_cmd.py, start_cmd.py, status_cmd.py, queue_cmd.py
  - [x] Register `queue` as sub-app via `app.add_typer(queue_app, name="queue")`
  - [x] Each command stub should have a docstring and print "Not yet implemented"
  - [x] Verify `hpnc --help` shows all commands
- [x] Task 4: Configure development tooling (AC: 6, 7, 8, 9)
  - [x] Configure ruff in `pyproject.toml` (see Dev Notes for exact config)
  - [x] Configure mypy strict mode in `pyproject.toml`
  - [x] Configure pytest in `pyproject.toml`
  - [x] Create `.pre-commit-config.yaml` with ruff lint, ruff format, and mypy hooks
  - [x] Create `.gitignore` for Python, uv, IDE artifacts
  - [x] Create `LICENSE` with MIT text
- [x] Task 5: Create test directory structure (AC: 13)
  - [x] Create `tests/conftest.py` (global fixtures, initially empty with docstring)
  - [x] Create `tests/unit/conftest.py` and mirror structure: core/, agents/, gates/, reporting/, schemas/, infra/
  - [x] Create `tests/integration/conftest.py`
  - [x] Create `tests/e2e/` directory
  - [x] Create `tests/fixtures/` with subdirectories: stories/, configs/, queues/, runs/
  - [x] Create minimal fixture files (valid_night_ready.md, default_config.yaml)
- [x] Task 6: Verify all tooling passes (AC: 12)
  - [x] Run `ruff check src/ tests/` — must pass with zero errors
  - [x] Run `mypy --strict src/` — must pass with zero errors
  - [x] Run `pytest` — must pass (no tests yet is OK, or add a trivial smoke test)
  - [x] Run `hpnc --help` — must display Typer-generated help

## Dev Notes

### Critical Architecture Decisions

- **src layout (`src/hpnc/`)**: Required for import safety. Without `src/`, tests import local source instead of installed package. Non-negotiable.
- **uv as build backend**: `uv_build` in `[build-system]`. Users still install via `pip install hpnc` or `pipx install hpnc`.
- **Typer for CLI**: Auto-generates `--help` and shell completion. `queue` is a sub-app, rest are top-level commands.
- **All stubs must type-check**: Even stub files must pass `mypy --strict`. Use `...` (Ellipsis) for Protocol method bodies, `pass` or placeholder Rich output for CLI commands.

### pyproject.toml Configuration

```toml
[build-system]
requires = ["uv>=0.5"]
build-backend = "uv_build"

[project]
name = "hpnc"
version = "0.1.0"
description = "Human-Planned Night Crew — overnight AI-powered task automation"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.12"
dependencies = [
    "typer>=0.14",
    "rich>=13.0",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "ruff>=0.8",
    "mypy>=1.12",
]

[project.scripts]
hpnc = "hpnc.cli.app:main"

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "--cov=src/hpnc --cov-report=term-missing"
```

### CLI App Structure

```python
# src/hpnc/cli/app.py
import typer

app = typer.Typer(name="hpnc", help="Human-Planned Night Crew — overnight AI task automation")
queue_app = typer.Typer(help="Manage the night queue")
app.add_typer(queue_app, name="queue")

@app.command()
def init() -> None:
    """Initialize HPNC in the current project."""
    ...

@app.command()
def validate() -> None:
    """Run pre-flight validation checks."""
    ...

@app.command()
def start(
    at: str | None = None,
    delay: str | None = None,
    dry_run: bool = False,
    mock: bool = False,
) -> None:
    """Start a night run."""
    ...

@app.command()
def status() -> None:
    """Show morning report — what happened last night."""
    ...

@queue_app.command()
def add(story: str = typer.Argument(..., help="Path to story file")) -> None:
    """Add a story to the night queue."""
    ...

def main() -> None:
    """Entry point for hpnc CLI."""
    app()
```

### __init__.py Exports (Per Package)

Each `__init__.py` must define `__all__` with the public API for that package. For stubs, export the names that will exist once the module is filled:

- `hpnc/__init__.py`: `__all__ = ["__version__"]` + version string
- `hpnc/cli/__init__.py`: `__all__ = ["app"]`
- `hpnc/core/__init__.py`: `__all__: list[str] = []` (empty for now, filled in Story 1.2+)
- `hpnc/agents/__init__.py`: `__all__: list[str] = []`
- `hpnc/gates/__init__.py`: `__all__: list[str] = []`
- `hpnc/reporting/__init__.py`: `__all__: list[str] = []`
- `hpnc/events/__init__.py`: `__all__: list[str] = []`
- `hpnc/infra/__init__.py`: `__all__: list[str] = []`
- `hpnc/schemas/__init__.py`: `__all__: list[str] = []`

### Pre-Commit Config

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff lint
        entry: ruff check
        language: system
        types: [python]
        stages: [pre-commit]
      - id: ruff-format
        name: ruff format
        entry: ruff format --check
        language: system
        types: [python]
        stages: [pre-commit]
      - id: mypy
        name: mypy
        entry: mypy src/
        language: system
        types: [python]
        stages: [pre-commit]
        pass_filenames: false
```

### Naming Conventions (Mandatory)

- Python: PEP 8 — `snake_case` functions, `PascalCase` classes, `UPPER_SNAKE` constants
- Files: `snake_case` — `task_runner.py`, `state_machine.py`
- YAML keys: `snake_case` — `night_ready`, `merge_target`
- CLI: lowercase commands, `--kebab-case` flags
- Docstrings: Google-Style (mandatory on all public functions)
- Type annotations: All public functions fully typed, `pathlib.Path` for all paths (never `str`)

### Forbidden Patterns

- No `print()` — all output through Rich console or logging
- No `shell=True` in subprocess calls
- No bare `raise Exception` — use `HpncError` subclasses
- No raw `open()` on state files — use `Workspace` (future stories)
- No magic strings — use Enums and constants
- No bare `# TODO` — always `# TODO(phase-N): description`

### Windows Compatibility (NFR28-30)

- Use `pathlib.Path` everywhere, never hardcoded separators
- Be aware of case-insensitive filesystem
- Test that all paths work on Windows

### Project Structure Notes

- This is a greenfield project — no existing code to integrate with
- The complete directory structure from Architecture must be created exactly as specified
- All stub files must be valid Python that passes `ruff check` and `mypy --strict`
- The `tests/fixtures/` directory should contain minimal example files for future test stories

### References

- [Source: architecture.md#Starter Template Evaluation] — uv selection rationale
- [Source: architecture.md#Project Module Structure] — complete module tree
- [Source: architecture.md#Complete Project Directory Structure] — full file listing
- [Source: architecture.md#Walking Skeleton] — Story 1 completion checklist
- [Source: architecture.md#Naming Patterns] — all naming conventions
- [Source: architecture.md#Code Conventions] — docstrings, types, imports
- [Source: architecture.md#Implementation Patterns] — enforcement rules
- [Source: prd.md#Technology Stack] — dependency choices
- [Source: prd.md#Command Structure] — CLI command tree
- [Source: prd.md#Shell Completion] — FR8 requirements

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

- uv 0.11.3 installed via pip, accessed as `python -m uv`
- `uv init --package --python 3.12 --name hpnc` used in existing repo (no subdirectory created)
- `uv sync` required after pyproject.toml entry point change to update installed package

### Completion Notes List

- All 6 tasks completed successfully
- Project initialized with uv 0.11.3, Python 3.12.13
- Dependencies: typer 0.24.1, rich 14.3.3, pyyaml 6.0.3
- Dev deps: pytest 9.0.2, pytest-cov 7.1.0, ruff 0.15.9, mypy 1.20.0
- Complete src/hpnc/ structure with 8 subpackages, all __init__.py with __all__
- CLI skeleton: 5 commands (init, validate, start, status, queue add) via Typer
- `hpnc --help` shows all commands correctly
- ruff check: All checks passed (18 files)
- mypy --strict: No issues found (18 files)
- pytest: 1 passed (smoke test)
- Added smoke test (test_version_exists) since pytest requires at least 1 test
- Note: uv uses `dependency-groups` instead of `project.optional-dependencies` — followed uv's convention
- Note: CLI command stubs use `typer.echo()` — will be replaced with Rich output in later stories

### Change Log

- 2026-04-06: Story 1.1 implementation complete — all ACs satisfied

### File List

- pyproject.toml (modified — added metadata, tool config, entry point)
- .python-version (created by uv)
- .gitignore (created)
- .pre-commit-config.yaml (created)
- uv.lock (auto-generated by uv)
- src/hpnc/__init__.py (modified — version + __all__)
- src/hpnc/__main__.py (created)
- src/hpnc/constants.py (created)
- src/hpnc/py.typed (created)
- src/hpnc/cli/__init__.py (created)
- src/hpnc/cli/app.py (created)
- src/hpnc/cli/init_cmd.py (created)
- src/hpnc/cli/validate_cmd.py (created)
- src/hpnc/cli/start_cmd.py (created)
- src/hpnc/cli/status_cmd.py (created)
- src/hpnc/cli/queue_cmd.py (created)
- src/hpnc/core/__init__.py (created)
- src/hpnc/core/__main__.py (created)
- src/hpnc/agents/__init__.py (created)
- src/hpnc/gates/__init__.py (created)
- src/hpnc/reporting/__init__.py (created)
- src/hpnc/events/__init__.py (created)
- src/hpnc/infra/__init__.py (created)
- src/hpnc/schemas/__init__.py (created)
- tests/conftest.py (created)
- tests/unit/conftest.py (created)
- tests/unit/test_smoke.py (created)
- tests/integration/conftest.py (created)
- tests/fixtures/stories/valid_night_ready.md (created)
- tests/fixtures/configs/default_config.yaml (created)
