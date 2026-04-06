# Story 3.4: Validation Engine & hpnc validate

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

Pre-flight validation checks: night_ready, mandatory frontmatter fields, blocking_questions, worktree availability, secrets hook, agent connectivity. Reports ALL failures with what/why/action (NFR24). Pure read-only (NFR15).

## Implementation Notes

- `core/validator.py`: Validator class with `validate_queue()` + individual check methods
- `cli/validate_cmd.py`: Rich-formatted pass/fail output
- Agent connectivity check added later (reads config to determine which agents to check)
- 10 unit tests covering all validation scenarios

## Review Findings

- Validator boolean bypass in mandatory check (night_ready/tests_required) — deferred
- parse_frontmatter silently swallows YAML errors — deferred
- Agent names were initially hardcoded, fixed to read from config

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/core/validator.py (created)
- src/hpnc/cli/validate_cmd.py (replaced stub)
- src/hpnc/core/__init__.py (modified)
- tests/unit/core/test_validator.py (created)
