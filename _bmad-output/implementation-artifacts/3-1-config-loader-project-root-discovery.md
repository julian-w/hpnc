# Story 3.1: Config Loader & Project Root Discovery

Status: done

## Story

As a developer,
I want HPNC to find my project root automatically and load configuration with sensible defaults,
so that all `hpnc` commands work from any subdirectory within my project.

## Acceptance Criteria

1. `ConfigLoader.find_root()` searches upward from CWD until it finds `_hpnc/config.yaml` (FR7)
2. If no `_hpnc/config.yaml` is found, a `ConfigError` is raised with what/why/action explaining how to run `hpnc init`
3. `ConfigLoader.load()` parses YAML and merges with built-in defaults (FR5, FR6)
4. Missing optional fields use defaults, missing mandatory fields raise `ConfigError`
5. The resulting `Config` object provides typed access to all configuration values
6. All paths in config are resolved as `pathlib.Path` relative to project root (NFR29)
7. Tests verify upward search finds root from nested directories
8. Tests verify default merging behavior
9. Tests verify error for missing config file
10. Tests verify error for malformed YAML

## Tasks / Subtasks

- [x] Task 1: Expand Config dataclass in `src/hpnc/infra/config.py` (AC: 5, 6)
  - [x] Keep existing fields: `project_name`, `project_root`, `merge_target`, `log_verbosity`, `agent_output`
  - [x] Add Phase 1 defaults: `merge_target: str = "main"`, `timeout: str = "30m"`, `max_fix_attempts: int = 3`
  - [x] Add `executor: str = "opus"`, `reviewer: str = "codex"`
  - [x] Add `protected_paths: list[str]` with default `["_hpnc/", "_bmad/", ".claude/"]`
  - [x] All Path fields resolved relative to `project_root`

- [x] Task 2: Implement ConfigLoader.find_root() (AC: 1, 2)
  - [x] Replace `NotImplementedError` stub with real implementation
  - [x] Start from `start` parameter (default: `Path.cwd()`)
  - [x] Walk upward checking for `_hpnc/config.yaml` at each level
  - [x] Stop at filesystem root
  - [x] Raise `ConfigError(what="HPNC project not found", why="No _hpnc/config.yaml found...", action="Run 'hpnc init' to initialize")` if not found

- [x] Task 3: Implement ConfigLoader.load() (AC: 3, 4, 5, 6)
  - [x] Replace `NotImplementedError` stub with real implementation
  - [x] Read `_hpnc/config.yaml` via `Workspace.read_yaml()` or direct yaml.safe_load
  - [x] Define `_DEFAULTS` dict with all default values
  - [x] Merge: file values override defaults, missing optionals get defaults
  - [x] Validate mandatory field: `project_name` must be present
  - [x] Resolve `project_root` as absolute Path
  - [x] Return `Config` dataclass instance

- [x] Task 4: Write unit tests (AC: 7, 8, 9, 10)
  - [x] File: `tests/unit/infra/test_config.py`
  - [x] `test_find_root_from_project_root` — finds config at current level
  - [x] `test_find_root_from_nested_subdir` — finds config from sub/sub/dir
  - [x] `test_find_root_missing_raises_config_error` — no config anywhere raises ConfigError
  - [x] `test_load_merges_defaults` — missing optional fields get defaults
  - [x] `test_load_file_overrides_defaults` — file values take precedence
  - [x] `test_load_missing_project_name_raises` — mandatory field missing raises ConfigError
  - [x] `test_load_malformed_yaml_raises` — invalid YAML raises ConfigError
  - [x] `test_load_resolves_project_root_as_path` — project_root is absolute Path

- [x] Task 5: Verify everything passes (AC: all)
  - [x] Run `ruff check src/ tests/` — zero errors
  - [x] Run `mypy --strict src/` — zero errors
  - [x] Run `pytest -v` — all tests pass (83 existing + new)

## Dev Notes

### Critical Architecture Decisions

- **Upward search pattern**: Start from given dir, check for `_hpnc/config.yaml`, move to parent, repeat. Stop at filesystem root (when `path == path.parent`). This is the standard project-root discovery pattern used by tools like git, cargo, npm.

- **Default merging, not deep merge**: Simple dict update — file values override defaults at top level. No recursive/deep merge needed for Phase 1 config structure.

- **Config is a dataclass, not a dict**: Typed access via attributes (`config.merge_target`) not dict keys (`config["merge_target"]`). mypy catches typos at compile time.

- **ConfigLoader reads directly, not via Workspace**: ConfigLoader is in `infra/` alongside Workspace. It reads `config.yaml` directly with `yaml.safe_load()` because Workspace depends on Config (circular dependency if ConfigLoader uses Workspace).

### Config Defaults

```python
_DEFAULTS: dict[str, Any] = {
    "merge_target": "main",
    "log_verbosity": "normal",
    "agent_output": "full",
    "timeout": "30m",
    "max_fix_attempts": 3,
    "executor": "opus",
    "reviewer": "codex",
    "protected_paths": ["_hpnc/", "_bmad/", ".claude/"],
}
```

### Import Rules

- `infra/config.py` may import from: `infra/errors.py`, `yaml`, stdlib only
- Must NOT import from Workspace (circular dependency)

### Previous Story Intelligence

- **Config dataclass** already exists with: `project_name`, `project_root`, `merge_target`, `log_verbosity`, `agent_output`
- **ConfigLoader stub** has `find_root()` and `load()` raising `NotImplementedError("Implemented in Story 2.1")` — note: the message says 2.1 but this is Story 3.1
- **ConfigError** available from `infra/errors.py` (exit code 4)
- **Workspace.read_yaml()** available but should NOT be used here (circular dep)
- **83 existing tests** — must not regress
- **Story file hygiene**: mark all checkboxes, fill Dev Record properly (Epic 2 retro action item)

### References

- [Source: architecture.md#Config Loader] — project root discovery, YAML parsing, default merging
- [Source: architecture.md#Three Levels of Configurable Values] — Constant, Default, Config
- [Source: architecture.md#Cross-Cutting Concerns] — project root discovery pattern
- [Source: epics.md#Story 3.1] — acceptance criteria
- [Source: prd.md#Project Setup & Configuration] — FR1-FR7

## Dev Agent Record

### Agent Model Used

Claude Opus 4.6 (1M context)

### Debug Log References

### Completion Notes List

- Config dataclass expanded: +5 fields (timeout, max_fix_attempts, executor, reviewer, protected_paths)
- ConfigLoader.find_root(): upward search, stops at filesystem root, ConfigError with actionable message
- ConfigLoader.load(): yaml.safe_load, default merging, mandatory field validation, Path resolution
- 8 new tests: find_root (3), load (5), config.py 96% coverage
- 91 total tests pass, ruff clean, mypy --strict clean

### Change Log

- 2026-04-06: Story 3.1 implementation complete

### File List

- src/hpnc/infra/config.py (replaced stub — full ConfigLoader + expanded Config)
- tests/unit/infra/test_config.py (created — 8 tests)
