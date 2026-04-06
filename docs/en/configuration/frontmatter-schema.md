# Frontmatter Schema Reference

Story files use YAML frontmatter between `---` delimiters to provide metadata for HPNC.

## Schema

| Field | Type | Required | Default | Validation |
|-------|------|----------|---------|------------|
| `night_ready` | bool | Yes | `false` | Must be `true` for night run |
| `executor` | string | Yes | `""` | Must be a known agent: opus, codex, mock |
| `reviewer` | string | Yes | `""` | Must be a known agent, different from executor |
| `risk` | string | No | `low` | low, medium, high |
| `tests_required` | bool | Yes | `true` | Must be defined |
| `touches` | list[str] | No | `[]` | Abstract resource names |
| `blocking_questions` | list[str] | No | `[]` | Must be empty for night-ready |
| `gates_required` | list[str] | Yes | `[]` | Known gates: build, tests, lint |

## Validation rules

`hpnc validate` checks:

1. `night_ready` is `true`
2. All mandatory fields are present and non-empty
3. `blocking_questions` is empty
4. All `gates_required` values are recognized

## Known gates (Phase 1)

- `build` — project builds/imports successfully
- `tests` — test suite passes
- `lint` — linter passes (ruff, eslint, etc.)
