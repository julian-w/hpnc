# Story 5.1: Claude Code Executor

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

ClaudeCodeExecutor implements AgentExecutor Protocol. Invokes Claude Code CLI (`claude`) in non-interactive mode for task implementation and review.

## CLI Research & Decisions

**Claude Code CLI Reference** (verified against actual docs + live testing):

```bash
claude -p "prompt" \
  --dangerously-skip-permissions \
  --output-format text \
  --max-turns 10 \
  --no-session-persistence \
  --append-system-prompt-file instructions.md \
  --model claude-sonnet-4-5-20250514
```

### Key Findings:
- `-p` (or `--print`): Non-interactive mode — REQUIRED for subprocess usage
- `--bare`: Skips auth auto-discovery — **breaks authentication**, removed after testing
- `--no-session-persistence`: Don't clutter disk with abandoned sessions
- `--dangerously-skip-permissions`: Required for autonomous file editing + command execution
- `--append-system-prompt-file`: Adds executor instructions without replacing system prompt
- `--output-format text`: Plain text output (json also available)
- `--max-turns N`: Safety limit for agentic loops
- `--model`: Optional model override from config
- Story content passed as `-p` argument (no `--input-file` flag exists)
- `stdin=DEVNULL`: Prevents interactive prompts

### What didn't work:
- `--bare` flag: Disables auth detection, Claude reports "Not logged in"
- Passing story as positional argument: Must use `-p "content"`

## Preflight Check

Verifies before night run:
1. CLI installed (`claude --version`)
2. Authenticated (prompt completes with exit 0)
3. Can create files (marker file `.hpnc-preflight-test`)
4. Can execute commands (`echo COMMAND_OK` verified in output)

Cleanup: marker deleted in `finally` block. Timeout: 120s.

## Implementation Notes

- `agents/claude_code.py`: ClaudeCodeExecutor class
- `check_connectivity()`: static method, --version check
- `preflight_check()`: static method, file creation + command execution
- `start()`: reads story content, builds claude command, returns Popen
- `stream_output()`: yields lines from stdout
- `get_exit_status()`: 0=SUCCESS, else=FAILURE (simplified from 3-way mapping)
- Model from `config.executor_model` or `config.reviewer_model` (role-agnostic)

## E2E Tests (pytest.mark.e2e, skipped in CI)

- `test_claude_code_connectivity` — PASS
- `test_claude_code_simple_prompt` — PASS (response received)
- `test_claude_code_preflight_creates_file_and_runs_command` — PASS

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/agents/claude_code.py (created)
- src/hpnc/agents/__init__.py (modified)
- tests/e2e/test_agent_smoke.py (created)
