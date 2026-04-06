# Night Policy

## The Two-Layer Release Model

HPNC uses two layers to control what runs overnight:

### Layer 1: Story Frontmatter (may run)

The `night_ready: true` flag in a story's frontmatter declares that this task is prepared for autonomous execution. Required fields:

- `executor` — which AI agent implements (opus, codex)
- `reviewer` — which AI agent reviews (different from executor)
- `tests_required` — tests must be defined
- `gates_required` — quality gates to pass
- `blocking_questions` — must be empty

### Layer 2: Night Queue (should run tonight)

Adding a story to `_hpnc/night-queue.yaml` via `hpnc queue add` schedules it for the next run. The queue controls timing and order.

## Cross-Model Review

The reviewer is never the executor. If Claude Code implements, Codex reviews — and vice versa. This catches blind spots that the implementing model would miss.

## Quality Gates

Every task must pass all configured gates before reaching `done`:

- **build** — project compiles/imports without errors
- **tests** — test suite passes
- **lint** — code quality checks pass

A gate only passes when the subprocess exits with code 0. No false positives.

## Worktree Isolation

Each task runs in its own Git worktree on a `night/<task-name>` branch. The main branch is never modified directly. Worktrees are cleaned up after completion regardless of outcome.
