# State Machine

Every task moves through a defined set of states during a night run.

## Phase 1 States

```
QUEUED → SETUP_WORKTREE → IMPLEMENTATION → REVIEW → GATES → DONE
                ↓                ↓            ↓           ↓
              FAILED          BLOCKED      BLOCKED      FAILED
```

| State | Description |
|-------|-------------|
| `queued` | Task is in the night queue, waiting to be processed |
| `setup_worktree` | Creating Git branch and worktree |
| `implementation` | AI executor agent is working on the task |
| `review` | AI reviewer agent is reviewing the implementation |
| `gates` | Quality gates (build, tests, lint) are running |
| `done` | All gates passed — task is complete |
| `failed` | A quality gate failed |
| `blocked` | Agent could not proceed — needs human input |

## Terminal States

`done`, `failed`, and `blocked` are terminal — no further transitions are possible.

## Phase 2 States (planned)

| State | Description |
|-------|-------------|
| `fix_attempt` | Agent is retrying after review feedback |
| `paused` | Waiting for API rate limit to reset |
| `awaiting_review` | Implementation complete, waiting for review |
| `proposal` | Human review required before merge |
| `merged` | Task branch merged into target |
| `interrupted` | Process was terminated unexpectedly |

## Transition Rules

Transitions are enforced by a pure function — invalid transitions raise `InvalidTransitionError`. The state machine has no I/O and no side effects.
