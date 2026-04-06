# hpnc start

Start a night run.

## Usage

```bash
hpnc start [OPTIONS]
```

## Options

| Flag | Description | Example |
|------|-------------|---------|
| `--mock` | Use mock agents (no tokens) | `hpnc start --mock` |
| `--dry-run` | Show what would happen, no execution | `hpnc start --dry-run` |
| `--at HH:MM` | Schedule start time (local time) | `hpnc start --at 23:00` |
| `--delay Ns/m/h` | Wait before starting | `hpnc start --delay 30m` |

`--at` and `--delay` are mutually exclusive.

## What happens

1. **Pre-flight** — verifies agents can authenticate, edit files, and run commands
2. **Dispatcher** — acquires lock, processes queue sequentially
3. **Per task** — creates worktree, runs executor, runs reviewer, runs gates
4. **Cleanup** — removes worktrees, empties queue, writes state

## Pre-flight checks

Before the night run, HPNC verifies each configured agent:

- Creates a test file (file editing capability)
- Runs `echo COMMAND_OK` (command execution capability)
- Cleans up the test file

This costs a few tokens but prevents empty nights.

## Exit codes

- `0` — all tasks done
- `1` — one or more tasks failed or blocked
