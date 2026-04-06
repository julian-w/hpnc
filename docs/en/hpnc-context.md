# HPNC — Human-Planned Night Crew

LLM-optimized context file. Generated from docs/en/.

# HPNC — Human-Planned Night Crew

*Humans plan by day. Agents implement by night.*

HPNC builds the orchestration and quality assurance layer that turns AI coding from interactive babysitting into autonomous overnight execution.

## How it works

1. **Plan** — structure work as stories with machine-readable frontmatter using [BMad](https://github.com/bmadcode/BMAD-METHOD)
2. **Queue** — add stories to the night queue: `hpnc queue add story.md`
3. **Validate** — pre-flight checks: `hpnc validate`
4. **Run** — start the night run: `hpnc start`
5. **Review** — check results in the morning: `hpnc status`

## Quick install

```bash
pip install hpnc
hpnc init
```

## Architecture

```
Story File (.md)
  → Queue Manager (parse frontmatter)
  → Validator (check night-ready)
  → Dispatcher (orchestrate)
  → Task Runner:
      → Git (create worktree + branch)
      → AgentExecutor (implement)
      → AgentExecutor (review)
      → Quality Gates (build, tests, lint)
      → Event Listener (write run.yaml)
  → Report Generator
  → CLI (morning report)
```

## For AI Agents

Need a single context file for your AI agent? See [HPNC.md (AI Context)](hpnc-context.md) — auto-generated, LLM-optimized.

# Getting Started

## Prerequisites

- Python 3.12+
- Git 2.20+
- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- [Codex](https://openai.com/codex) CLI installed and authenticated (optional)

## Installation

```bash
pip install hpnc
```

Or for development:

```bash
git clone https://github.com/julian-w/hpnc.git
cd hpnc
uv sync
```

## Initialize your project

```bash
cd your-project
hpnc init
```

This creates `_hpnc/` with:

- `config.yaml` — project configuration
- `executor-instructions.md` — rules for AI agents
- `night-queue.yaml` — empty task queue

## Prepare a story

Create a story file with night-ready frontmatter:

```markdown
---
night_ready: true
executor: opus
reviewer: codex
risk: low
tests_required: true
blocking_questions: []
gates_required:
  - build
  - tests
  - lint
---

# My Task

As a developer, I want...
```

## Add to queue and validate

```bash
hpnc queue add stories/my-task.md
hpnc validate
```

## Run

```bash
# Test with mock agents first
hpnc start --mock

# Real night run
hpnc start

# Schedule for tonight
hpnc start --at 23:00
```

## Check results

```bash
hpnc status
```

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

# hpnc init

Initialize HPNC in the current project.

## Usage

```bash
hpnc init
```

## What it does

1. Creates `_hpnc/` directory
2. Writes `config.yaml` with project name detected from directory
3. Writes `executor-instructions.md` template
4. Writes `night-queue.yaml` (empty queue)
5. Checks Claude Code and Codex CLI connectivity
6. Detects existing BMad configuration

## Safe to re-run

Running `hpnc init` on an already initialized project:

- **Never overwrites** existing `config.yaml`
- Creates missing files only
- Always runs connectivity checks

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

# hpnc status

Show the morning report — what happened last night.

## Usage

```bash
hpnc status
```

## Output

A Rich-formatted table showing:

| Column | Description |
|--------|-------------|
| Task | Task name from story file |
| Status | done (green), failed (red), blocked (yellow) |
| Executor | Which agent implemented |
| Reviewer | Which agent reviewed |

## Failed tasks

Shows the failure reason and recommended action:

```
FAILED: login-validation
  Gate 'tests' failed: exit code 1
  → Review gate output and fix issues
```

## Blocked tasks

Shows the blocking reason and recommended action:

```
BLOCKED: api-refactor
  Agent could not proceed
  → Review story requirements and unblock manually
```

## Report file

A markdown report is saved to `_hpnc/reports/`.

# hpnc queue

Manage the night queue.

## hpnc queue add

Add a story to the night queue.

```bash
hpnc queue add stories/my-task.md
```

### What it does

1. Validates the file exists and is `.md`
2. Parses YAML frontmatter
3. Checks for duplicates (by file path)
4. Appends to `_hpnc/night-queue.yaml`
5. Shows confirmation with metadata summary

### Duplicate detection

Adding the same story twice is rejected with a warning.

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
