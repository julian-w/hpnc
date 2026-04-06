# HPNC — Human-Planned Night Crew

*Humans plan by day. Agents implement by night.*

Overnight AI-powered task automation built on the [BMad Method](https://github.com/bmadcode/BMAD-METHOD). Plan stories with structured frontmatter during the day, let AI agents (Claude Code, Codex) implement in isolated Git worktrees at night with cross-model review and quality gates, review merge-ready results in the morning.

## What is HPNC?

HPNC turns unused AI token budgets and overnight hours into reviewed, tested, merge-ready code. You structure and clarify work during the day using BMad as the planning framework. At night, a crew of AI agents autonomously implements fully prepared tasks in isolated Git worktrees, runs cross-model reviews, executes quality gates, and delivers results by morning.

**The core insight:** the problem with AI-assisted coding was never "AI can't code." It was that nobody built the orchestration and quality assurance layer around it.

### Key Features

- **Structured planning artifacts** — tasks enter the pipeline as stories with machine-readable frontmatter, not loose prompts
- **Cross-model review** — reviewer is never the executor, catching blind spots a single model would miss
- **Quality gates** — build, tests, and lint must pass before any task reaches `done`
- **Morning-ready results** — status reports, reviewed branches, test results, and clear next steps
- **Token-free development** — mock executor enables full end-to-end testing without API calls

## Installation

Requires Python 3.12+.

```bash
pip install hpnc
```

Or for development:

```bash
git clone https://github.com/your-username/hpnc.git
cd hpnc
uv sync
```

## Quick Start

```bash
# Initialize HPNC in your project
hpnc init

# Add a story to the night queue
hpnc queue add stories/my-task.md

# Run pre-flight validation
hpnc validate

# Start a night run (use --mock for testing)
hpnc start --mock

# Check results in the morning
hpnc status
```

## CLI Commands

| Command | Description |
|---|---|
| `hpnc init` | Initialize HPNC in the current project |
| `hpnc validate` | Run pre-flight validation checks |
| `hpnc start` | Start a night run (`--at`, `--delay`, `--dry-run`, `--mock`) |
| `hpnc status` | Show morning report |
| `hpnc queue add` | Add a story to the night queue |

## How It Works

```
Story File (.md)
  -> Queue Manager (parse frontmatter)
  -> Validator (check night-ready)
  -> Dispatcher (orchestrate)
  -> Task Runner:
      -> Git (create worktree + branch)
      -> AgentExecutor (implement)
      -> AgentExecutor (review)
      -> Quality Gates (build, tests, lint)
      -> Event Listener (write run.yaml)
  -> Report Generator
  -> CLI (morning report)
```

## Development Status

HPNC is under active development. Current status:

- [x] **Epic 1: Project Foundation** — Package structure, state machine, interfaces, mock executor, CI pipeline
- [ ] **Epic 2: Task Execution Engine** — Workspace, quality gates, event system, task runner
- [ ] **Epic 3: Setup, Validation & Queue** — Config loader, init command, queue manager, validation
- [ ] **Epic 4: Night Run & Morning Review** — Dispatcher, scheduling, report generator
- [ ] **Epic 5: Real Agent Integration** — Claude Code executor, Codex executor
- [ ] **Epic 6: Documentation** — MkDocs site, executor instructions

## Tech Stack

- **Language:** Python 3.12+
- **CLI:** Typer + Rich
- **Package Manager:** uv
- **Testing:** pytest + mypy --strict + ruff
- **CI:** GitHub Actions (Ubuntu + Windows)

## License

MIT
