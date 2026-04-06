# Getting Started

## Prerequisites

- Python 3.12+
- Git 2.20+
- [Claude Code](https://claude.ai/code) CLI installed and authenticated
- [Codex](https://openai.com/codex) CLI installed and authenticated (optional)

## Installation

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
