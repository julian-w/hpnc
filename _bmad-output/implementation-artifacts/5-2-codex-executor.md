# Story 5.2: Codex Executor

Status: done

> Implemented in fast-track mode without full story spec. See epics.md for original ACs.

## Summary

CodexExecutor implements AgentExecutor Protocol. Invokes Codex CLI (`codex exec`) for task implementation and review.

## CLI Research & Decisions

**Codex CLI Reference** (from https://developers.openai.com/codex/cli/reference + live testing):

```bash
codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  -C /path/to/worktree \
  -m gpt-5.4 \
  "Implement the story requirements"
```

### Key Flags:
- `exec`: Non-interactive subcommand (vs interactive TUI)
- `--dangerously-bypass-approvals-and-sandbox` (`--yolo`): No approval prompts, no sandbox — **REQUIRED for unattended night runs**
- `--full-auto`: Sets `--sandbox workspace-write` + `--ask-for-approval on-request` — **NOT sufficient** for night runs (blocks on file writes with stdin closed)
- `-C <DIR>`: Explicit working directory (preferred over cwd for Codex)
- `-m <MODEL>`: Model override
- `--ephemeral`: Don't persist sessions
- `--json`: Machine-readable JSONL output
- `-o <FILE>`: Write last message to file
- `--skip-git-repo-check`: Allow running outside git repo

### Critical Discovery: `--full-auto` is NOT enough for night runs

```
--full-auto = --sandbox workspace-write + --ask-for-approval on-request
```

With `stdin=DEVNULL`, `on-request` approval blocks on file write operations. Tested:
- `--full-auto` + file creation prompt: **Hangs** (approval prompt with no stdin)
- `--full-auto` + echo command: Works (no approval needed)
- `--dangerously-bypass-approvals-and-sandbox` + file creation: **Works** (10s)

### `--ask-for-approval` is NOT a valid `exec` flag

Despite being documented as a top-level flag, `--ask-for-approval` / `-a` is NOT available in `codex exec`:
```
error: unexpected argument '--ask-for-approval' found
Usage: codex exec --sandbox <SANDBOX_MODE> [PROMPT]
```

Only `--dangerously-bypass-approvals-and-sandbox` works for bypassing approvals in exec mode.

### Windows .cmd Resolution

Codex is a Node.js package installed via npm. On Windows, `subprocess.run(["codex", ...])` fails with `FileNotFoundError` because Python doesn't resolve `.cmd` wrappers. Fix: `shutil.which("codex")` finds `codex.CMD`.

### Instructions via AGENTS.md

Codex has no `--instructions` flag. Instructions are auto-discovered from `AGENTS.md` files in the directory hierarchy. The executor copies the instructions file as `AGENTS.md` into the worktree before starting.

### Multi-line Prompts

Codex misinterprets Python multi-line strings (`\n` in f-strings) as questions rather than instructions. Single-line prompts work reliably.

## Preflight Check

Verifies before night run:
1. CLI installed (`codex --version` via shutil.which)
2. Authenticated (prompt completes with exit 0)
3. Can create files (marker file `.hpnc-preflight-test`)
4. Can execute commands (`echo COMMAND_OK` verified in output)

Uses `--dangerously-bypass-approvals-and-sandbox` for preflight (same as production run).
Cleanup: marker deleted in `finally` block. Timeout: 120s.

## Agent Routing

`agents/routing.py` maps frontmatter names to implementations:
- `"opus"` / `"claude"` → ClaudeCodeExecutor
- `"codex"` → CodexExecutor
- `"mock"` → MockAgentExecutor

Case-insensitive. Unknown names raise ConfigError. Empty/None input guarded.

## Implementation Notes

- `agents/codex.py`: CodexExecutor class + `_find_codex()` helper (shutil.which)
- `agents/routing.py`: get_executor() with registry pattern
- `check_connectivity()`: static method, --version via resolved path
- `preflight_check()`: static method, file creation + command execution
- `start()`: copies AGENTS.md, builds codex exec command, returns Popen
- `stdin=DEVNULL`: Prevents stdin reading ("Reading additional input from stdin...")
- Model from `config.reviewer_model` or `config.executor_model` (role-agnostic)

## E2E Tests (pytest.mark.e2e, skipped in CI)

- `test_codex_connectivity` — PASS
- `test_codex_simple_prompt` — PASS (response received)
- `test_codex_preflight_creates_file_and_runs_command` — PASS

## Dev Agent Record

### Agent Model Used
Claude Opus 4.6 (1M context)

### File List
- src/hpnc/agents/codex.py (created)
- src/hpnc/agents/routing.py (created)
- src/hpnc/agents/__init__.py (modified)
- src/hpnc/cli/start_cmd.py (modified — routing + preflight integration)
- tests/unit/agents/test_routing.py (created)
- tests/e2e/test_agent_smoke.py (created/extended)
