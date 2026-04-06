# Troubleshooting

## Common errors

### HPNC project not found

```
✗ HPNC project not found
  No _hpnc/config.yaml found in any parent directory
  Action: Run 'hpnc init' to initialize HPNC in your project
```

**Fix:** Run `hpnc init` in your project root.

### Agent CLI not found

```
✗ Claude Code (executor) not found
  'claude' command not found on PATH
```

**Fix:** Install the agent CLI:
- Claude Code: visit [claude.ai/code](https://claude.ai/code)
- Codex: `npm install -g @openai/codex`

### Agent preflight failed

```
✗ Claude Code preflight failed
  Not logged in · Please run /login
```

**Fix:** Run `claude` interactively and authenticate.

### Dispatcher lock already held

```
✗ Dispatcher lock already held
  Process 12345 holds the lock
```

**Fix:** Wait for the running dispatcher to finish, or delete `_hpnc/.dispatcher.lock` if the process crashed.

### Story not night-ready

```
✗ Story not night-ready
  night_ready is not set to true
```

**Fix:** Add `night_ready: true` to the story's YAML frontmatter.

### Blocking questions not resolved

```
✗ Blocking questions not resolved
  2 blocking question(s) remain
```

**Fix:** Answer all questions in the `blocking_questions` list and clear it.

### No secrets hook configured

```
✗ No secrets hook configured
  No git-secrets or gitleaks hook found
```

**Fix:** Add a secrets detection hook to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

## Performance

### Night run seems slow

- Check `max_turns` in config (default: 10). Lower = faster but less capable.
- Use `--mock` first to verify the pipeline works without token cost.
- Gate timeouts are 300s per gate. Long test suites may need adjustment.

### Worktrees not cleaned up

If worktrees remain after a crash, list and remove them:

```bash
git worktree list
git worktree remove <path> --force
```
