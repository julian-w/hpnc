# hpnc status

Show the morning report — what happened last night.

## Usage

```bash
hpnc status
```

## Output

A Rich-formatted table showing:

| Column | Description |
|--------|-------------|
| Task | Task name from story file |
| Status | done (green), failed (red), blocked (yellow) |
| Executor | Which agent implemented |
| Reviewer | Which agent reviewed |

## Failed tasks

Shows the failure reason and recommended action:

```
FAILED: login-validation
  Gate 'tests' failed: exit code 1
  → Review gate output and fix issues
```

## Blocked tasks

Shows the blocking reason and recommended action:

```
BLOCKED: api-refactor
  Agent could not proceed
  → Review story requirements and unblock manually
```

## Report file

A markdown report is saved to `_hpnc/reports/`.
