# Story 3.3: Queue Manager & hpnc queue add

Status: done

## Story

As a developer,
I want to add story files to the night queue via CLI,
so that I can prepare multiple tasks for overnight execution.

## Acceptance Criteria

1. Story file path is validated to exist and be a markdown file (FR9)
2. Story frontmatter is parsed to extract night-ready metadata (FR13)
3. The story is added to `_hpnc/night-queue.yaml` with its metadata (FR12)
4. Confirmation message shows the story was added with key metadata summary
5. System accepts any story file with valid frontmatter (FR17), missing optional fields use defaults
6. Duplicate story warns and does not add again
7. New story is appended to existing queue, preserving order
8. Tests verify frontmatter parsing with valid and invalid story files
9. Tests verify queue YAML read/write/append operations
10. Tests verify duplicate detection
11. Tests use fixture story files from `tests/fixtures/stories/`

## Tasks / Subtasks

- [ ] Task 1: Implement QueueManager in `src/hpnc/core/queue_manager.py` (AC: 1, 2, 3, 5, 6, 7)
  - [ ] Define `QueueManager` class with `workspace: Workspace`, `queue_path: Path` constructor
  - [ ] `parse_frontmatter(story: Path) -> FrontmatterSchema`: read story markdown, extract YAML frontmatter between `---` delimiters, parse into FrontmatterSchema
  - [ ] `add(story: Path) -> bool`: validate path exists + is .md, parse frontmatter, check duplicates, append to queue YAML, return True if added
  - [ ] `list_tasks() -> list[dict[str, Any]]`: read queue YAML and return task list
  - [ ] Queue YAML format: `tasks: [{story: "path", ...metadata}]`
  - [ ] Duplicate detection: check if story path already in queue
  - [ ] Missing optional frontmatter fields use defaults from FrontmatterSchema

- [ ] Task 2: Wire hpnc queue add CLI in `src/hpnc/cli/queue_cmd.py` (AC: 4)
  - [ ] Update `add()` command to call QueueManager.add()
  - [ ] Display Rich-formatted confirmation with metadata summary
  - [ ] Display warning for duplicates

- [ ] Task 3: Update fixture story files in `tests/fixtures/stories/` (AC: 11)
  - [ ] Update `valid_night_ready.md` with proper frontmatter
  - [ ] Create `missing_frontmatter.md` — no frontmatter block
  - [ ] Ensure existing fixtures are usable for queue tests

- [ ] Task 4: Write unit tests (AC: 8, 9, 10)
  - [ ] File: `tests/unit/core/test_queue_manager.py`
  - [ ] `test_parse_frontmatter_valid_story` — extracts all fields
  - [ ] `test_parse_frontmatter_missing_fields_uses_defaults` — optional fields default
  - [ ] `test_parse_frontmatter_no_frontmatter_returns_defaults` — no --- block
  - [ ] `test_add_story_to_empty_queue` — creates entry in queue
  - [ ] `test_add_story_appends_to_existing_queue` — preserves order
  - [ ] `test_add_duplicate_story_returns_false` — warns, doesn't add
  - [ ] `test_add_nonexistent_file_raises` — ConfigError for missing file
  - [ ] `test_add_non_markdown_raises` — ConfigError for .txt/.py files

- [ ] Task 5: Update exports and verify (AC: all)
  - [ ] Update `src/hpnc/core/__init__.py` with QueueManager export
  - [ ] Run `ruff check src/ tests/` — zero errors
  - [ ] Run `mypy --strict src/` — zero errors
  - [ ] Run `pytest -v` — all tests pass (97 existing + new)

## Dev Notes

### Critical Architecture Decisions

- **Frontmatter parsing**: Story files use YAML frontmatter between `---` delimiters (standard markdown convention). Parse the YAML block, map to FrontmatterSchema. Fields not present get defaults from the dataclass.

- **Queue is append-only in add**: `add()` reads existing queue, appends new entry, writes back atomically via Workspace. No reordering in Phase 1.

- **Duplicate detection by path**: Compare story file paths (resolved to absolute). Same file = duplicate.

- **QueueManager uses Workspace**: All YAML read/write goes through Workspace for atomic writes. Queue file is `_hpnc/night-queue.yaml`.

### Frontmatter Format

```markdown
---
night_ready: true
executor: opus
reviewer: codex
risk: low
tests_required: true
touches: [login, auth]
blocking_questions: []
gates_required: [build, tests, lint]
---

# Story Title
...
```

### Queue YAML Format

```yaml
tasks:
  - story: stories/login-task.md
    night_ready: true
    executor: opus
    reviewer: codex
    risk: low
  - story: stories/refactor-api.md
    night_ready: true
    executor: codex
    reviewer: opus
```

### Import Rules

- `core/queue_manager.py` may import from: `schemas/frontmatter.py`, `infra/workspace.py`, `infra/errors.py`, `yaml`, stdlib
- `cli/queue_cmd.py` may import from: `core/queue_manager.py`, `infra/config.py`, `rich`, `typer`

### Previous Story Intelligence

- **FrontmatterSchema** (1.2): dataclass with all 8 fields + defaults
- **Workspace** (2.1): read_yaml, write_yaml_atomic — use for queue file
- **ConfigLoader** (3.1): find_root + load for project discovery
- **Queue CLI stub** in `queue_cmd.py` has `add(story: str)` with typer.Argument
- **Fixture files**: `tests/fixtures/stories/valid_night_ready.md` exists but may need frontmatter update
- **97 existing tests** — must not regress

### References

- [Source: architecture.md#Queue Manager] — FR9-FR17, queue parsing
- [Source: architecture.md#Data Flow] — story file -> queue manager -> validator
- [Source: epics.md#Story 3.3] — acceptance criteria
- [Source: prd.md#Story & Queue Management] — FR9-FR17

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
