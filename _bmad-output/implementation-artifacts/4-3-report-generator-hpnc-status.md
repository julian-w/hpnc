# Story 4.3: Report Generator & hpnc status

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

Report Generator parses run.yaml artifacts, produces NightReport with task table, failed/blocked details with `->` recommended actions. `hpnc status` displays Rich-formatted terminal output, saves markdown report.

## Implementation Notes

- `reporting/generator.py`: ReportGenerator, TaskReport, NightReport dataclasses
- `cli/status_cmd.py`: Rich Table with colored status (green/red/yellow)
- Finds latest run via rglob + mtime sorting
- Saves markdown to `_hpnc/reports/`
- Handles "no runs found" gracefully
- 6 unit tests covering all scenarios

## Review Findings

- `hpnc status` always writes report file (side effect) — deferred
- FR67 (commit artifacts into task branch) not implemented — deferred Phase 2
- find_latest_run uses mtime not date — deferred

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/reporting/generator.py (created)
- src/hpnc/reporting/__init__.py (modified)
- src/hpnc/cli/status_cmd.py (replaced stub)
- tests/unit/reporting/__init__.py (created)
- tests/unit/reporting/test_generator.py (created)
