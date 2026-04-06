# Story 3.2: hpnc init Command

Status: done

## Story

As a developer,
I want to initialize HPNC in my existing repository with a single command,
so that I can start using HPNC with sensible defaults and verified connectivity.

## Acceptance Criteria

1. `_hpnc/` directory is created with `config.yaml` containing sensible defaults (FR1, FR5)
2. `_hpnc/executor-instructions.md` is created with a template for agent rules
3. `_hpnc/night-queue.yaml` is created as an empty queue file
4. Connectivity check verifies Claude Code CLI is installed and reachable via version check subprocess (FR2)
5. Connectivity check verifies Codex CLI is installed and reachable via version check subprocess (FR3)
6. Connectivity results displayed with clear pass/fail using Rich formatting
7. If an agent CLI is not found, a warning is shown (not fatal — agents may be installed later)
8. Existing BMAD configuration is detected and reported (FR4)
9. Output confirms successful initialization with next steps guidance
10. On re-init: existing configuration is NOT overwritten (NFR16)
11. On re-init: message informs project already initialized, connectivity check still runs
12. Tests verify directory and file creation
13. Tests verify existing config is preserved on re-init
14. Tests verify connectivity check output

## Tasks / Subtasks

- [x] Task 1: Implement init logic in `src/hpnc/cli/init_cmd.py` (AC: 1, 2, 3, 8, 9, 10, 11)
  - [x] Create `_hpnc/` directory if not exists
  - [x] Write `config.yaml` with defaults (project_name from git repo name or directory name) — only if file doesn't exist (NFR16)
  - [x] Write `executor-instructions.md` with template content — only if file doesn't exist
  - [x] Write `night-queue.yaml` with `tasks: []` — only if file doesn't exist
  - [x] Detect BMAD: check for `_bmad/` directory or `.claude/skills/bmad-*` and report
  - [x] Display Rich-formatted success message with next steps
  - [x] If already initialized: show "Already initialized" + still run connectivity check

- [x] Task 2: Implement connectivity checks (AC: 4, 5, 6, 7)
  - [x] Define `_check_cli(name: str, command: list[str]) -> bool` helper
  - [x] Check Claude Code: `claude --version` via subprocess.run
  - [x] Check Codex: `codex --version` via subprocess.run
  - [x] Display Rich pass/fail for each (green checkmark / yellow warning)
  - [x] Missing CLI = warning, not error (agents can be installed later)
  - [x] Catch `FileNotFoundError` for missing executables

- [x] Task 3: Wire into Typer CLI in `src/hpnc/cli/app.py` (AC: all)
  - [x] Update `init()` command to call the init logic
  - [x] Pass Rich console for formatted output

- [x] Task 4: Write tests (AC: 12, 13, 14)
  - [x] File: `tests/unit/cli/test_init_cmd.py`
  - [x] `test_init_creates_hpnc_directory` — _hpnc/ created with config, instructions, queue
  - [x] `test_init_config_has_project_name` — config.yaml contains project_name
  - [x] `test_init_preserves_existing_config` — re-init doesn't overwrite
  - [x] `test_init_executor_instructions_template` — file has content
  - [x] `test_init_connectivity_missing_cli_warns` — mock subprocess FileNotFoundError
  - [x] `test_init_detects_bmad` — _bmad/ present is detected

- [x] Task 5: Verify everything passes (AC: all)
  - [x] Run `ruff check src/ tests/` — zero errors
  - [x] Run `mypy --strict src/` — zero errors
  - [x] Run `pytest -v` — all tests pass (91 existing + new)

## Dev Notes

### Critical Architecture Decisions

- **NFR16 safe re-init**: NEVER overwrite existing files. Check existence before writing. Only create files that don't exist yet.

- **Connectivity = warning, not error**: Missing CLIs are expected during setup. Show yellow warning, not red error. The developer may install agents later.

- **Rich output for CLI**: Use `rich.console.Console` for formatted output. Green checkmarks, yellow warnings. This is the first CLI command with real output (previous were stubs).

- **Project name detection**: Try to derive from git remote name or fallback to directory name. Keep it simple.

### Init File Templates

```yaml
# _hpnc/config.yaml
project_name: {detected_name}
```

```markdown
# _hpnc/executor-instructions.md
# Executor Instructions for {project_name}

These instructions are provided to AI agents during night runs.

## Rules
- Follow the project's coding conventions
- Run tests before committing
- Do not modify files outside the task's worktree
```

```yaml
# _hpnc/night-queue.yaml
tasks: []
```

### Import Rules

- `cli/init_cmd.py` may import from: `infra/config.py`, `rich`, `subprocess`, stdlib
- CLI layer handles display, core logic stays testable

### Previous Story Intelligence

- **ConfigLoader** (3.1): fully implemented with find_root() and load()
- **CLI stub** in `init_cmd.py` currently prints "Not yet implemented"
- **Rich** (`rich>=13`) already a dependency
- **91 existing tests** — must not regress
- **Story file hygiene**: mark all checkboxes, fill Dev Record (Epic 2 retro action item)

### References

- [Source: architecture.md#CLI Structure] — init command
- [Source: architecture.md#Runtime Project Files] — _hpnc/ directory structure
- [Source: epics.md#Story 3.2] — acceptance criteria
- [Source: prd.md#Project Setup & Configuration] — FR1-FR5, NFR16

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
