# Story 4.2: Scheduling & hpnc start Command

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

`hpnc start` with --at (scheduled time), --delay (wait duration), --dry-run (no side effects), --mock (MockAgentExecutor). Wires Dispatcher with agent routing. Pre-flight agent checks before night run.

## Implementation Notes

- `cli/start_cmd.py`: Full implementation with scheduling, preflight, dispatcher wiring
- `_parse_delay()`: handles s/m/h suffixes, rejects negative values
- `_wait_until()`: local time, timedelta for month boundary safety, hibernate guard
- --at and --delay mutually exclusive
- --dry-run skips scheduling (no waiting)
- Pre-flight checks ALL configured agent types (not just hardcoded executor/reviewer)

## Review Findings (Multiple Rounds)

- Mock agent used even without --mock (deceptive ternary) — **fixed**, now uses agent routing
- --at month boundary crash (day+1 instead of timedelta) — **fixed**
- --at used UTC instead of local time — **fixed** to local time
- Run dir date format had slashes (created nested dirs) — **fixed** to dashes
- --at invalid format crashed with ValueError — **fixed** with validation
- Negative delay accepted — **fixed** with explicit check
- --at + --delay not mutually exclusive — **fixed**
- --dry-run waited for --at schedule — **fixed**, dry-run skips scheduling
- Preflight only checked executor=Claude, reviewer=Codex — **fixed**, checks all types
- Run number always "001" — **deferred** (auto-increment Phase 2)

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/cli/start_cmd.py (replaced stub)
- tests/unit/cli/test_start_cmd.py (created — 7 tests)
