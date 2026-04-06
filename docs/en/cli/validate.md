# hpnc validate

Run pre-flight validation checks before a night run.

## Usage

```bash
hpnc validate
```

## Checks performed

| Check | What | Failure action |
|-------|------|----------------|
| Night-ready | `night_ready: true` in frontmatter | Set flag in story |
| Mandatory fields | executor, reviewer, tests_required, gates_required | Add missing fields |
| Blocking questions | Must be empty | Resolve questions |
| Known gates | gates_required values are recognized | Use build, tests, lint |
| Worktree | Git worktrees can be created | Ensure git repo |
| Secrets hook | .pre-commit-config.yaml has git-secrets/gitleaks | Add secrets hook |
| Agent CLIs | Configured executor/reviewer CLIs on PATH | Install agents |

## Read-only operation

`hpnc validate` never modifies files. It only reads and reports.

## Exit codes

- `0` — all checks passed
- `1` — one or more checks failed
