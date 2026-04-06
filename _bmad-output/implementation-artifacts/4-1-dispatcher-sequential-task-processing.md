# Story 4.1: Dispatcher — Sequential Task Processing

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

Dispatcher orchestrates sequential task processing: acquires ProcessLock, iterates queue, runs each task through TaskRunner, persists state after each completion, cleans up queue.

## Implementation Notes

- `core/dispatcher.py`: Dispatcher class + DispatcherState for atomic state persistence
- ProcessLock context manager for exclusivity (NFR14)
- State saved to `_hpnc/dispatcher-state.yaml` after each task
- Queue emptied after all tasks complete (FR34)
- 4 integration tests: multi-task, state persistence, lock rejection, blocked tasks

## Review Findings (Epic 4 Review)

- Queue cleanup logic was initially broken (self-referencing set removed ALL tasks) — **fixed**
- No crash recovery logic (NFR12) — deferred to Phase 2
- task-spec.yaml not written, TaskRunner called in-process (simplified from architecture subprocess model)
- Queue blanked even on failure — by design, results are in run.yaml

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/core/dispatcher.py (created)
- src/hpnc/core/__init__.py (modified)
- tests/integration/test_dispatcher_flow.py (created)
