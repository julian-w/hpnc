# config.yaml Reference

Location: `_hpnc/config.yaml`

## All fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `project_name` | string | **required** | Project identifier |
| `merge_target` | string | `main` | Git branch for merges |
| `log_verbosity` | string | `normal` | Logging: minimal, normal, verbose |
| `agent_output` | string | `full` | Agent output capture: full, truncated, none |
| `timeout` | string | `30m` | Task timeout duration |
| `max_fix_attempts` | int | `3` | Fix-loop retry limit (Phase 2) |
| `executor` | string | `opus` | Default executor agent |
| `reviewer` | string | `codex` | Default reviewer agent |
| `executor_model` | string | `""` | Model override for executor |
| `reviewer_model` | string | `""` | Model override for reviewer |
| `max_turns` | int | `10` | Max agentic turns per task |
| `protected_paths` | list | `[_hpnc/, _bmad/, .claude/]` | Paths agents must not modify |

## Example

```yaml
project_name: my-app
merge_target: develop
executor: opus
reviewer: codex
executor_model: claude-sonnet-4-5-20250514
max_turns: 15
log_verbosity: verbose
protected_paths:
  - _hpnc/
  - _bmad/
  - .claude/
  - .env
```

## Agent identifiers

| Name | Agent | CLI |
|------|-------|-----|
| `opus` / `claude` | Claude Code | `claude` |
| `codex` | Codex | `codex` |
| `mock` | Mock (no tokens) | — |
