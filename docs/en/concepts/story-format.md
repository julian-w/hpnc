# Story Format

Stories are markdown files with YAML frontmatter that provides machine-readable metadata for HPNC.

## Frontmatter Fields

```yaml
---
night_ready: true          # Master switch for overnight execution
executor: opus             # Agent for implementation (opus, codex, mock)
reviewer: codex            # Agent for review (different from executor)
risk: low                  # Risk level: low, medium, high
tests_required: true       # Whether tests must be defined
touches:                   # Abstract resources affected
  - login
  - auth
blocking_questions: []     # Must be empty for night-ready
gates_required:            # Quality gates to run
  - build
  - tests
  - lint
---
```

## Required Fields

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `night_ready` | bool | Yes | `false` |
| `executor` | string | Yes | — |
| `reviewer` | string | Yes | — |
| `tests_required` | bool | Yes | `true` |
| `gates_required` | list | Yes | — |
| `risk` | string | No | `low` |
| `touches` | list | No | `[]` |
| `blocking_questions` | list | No | `[]` |

## Story Body

After the frontmatter, write the story in standard markdown. The body is passed to the AI agent as the implementation prompt.

```markdown
---
night_ready: true
executor: opus
reviewer: codex
gates_required: [build, tests, lint]
---

# Add Login Validation

As a developer, I want inline validation on the login form,
so that users see errors before submitting.

## Acceptance Criteria

1. Email field validates format on blur
2. Password field shows strength indicator
3. Submit button disabled until both fields valid
```
