# HPNC — Human-Planned Night Crew

!!! warning "Early Development"
    This project is under active development. APIs, CLI interfaces, and configuration formats may change at any time. Not yet recommended for production use.

*Humans plan by day. Agents implement by night.*

HPNC builds the orchestration and quality assurance layer that turns AI coding from interactive babysitting into autonomous overnight execution.

## How it works

1. **Plan** — structure work as stories with machine-readable frontmatter using [BMad](https://github.com/bmad-code-org/BMAD-METHOD)
2. **Queue** — add stories to the night queue: `hpnc queue add story.md`
3. **Validate** — pre-flight checks: `hpnc validate`
4. **Run** — start the night run: `hpnc start`
5. **Review** — check results in the morning: `hpnc status`

## Quick install

```bash
git clone https://github.com/julian-w/hpnc.git
cd hpnc
uv sync
hpnc init
```

**Requirements:** Python 3.12+, Git 2.20+, [Claude Code](https://claude.ai/code) and/or [Codex](https://openai.com/codex) CLI

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

Need a single context file for your AI agent? Download [HPNC.md](https://julian-w.github.io/hpnc/HPNC.md){:target="_blank"} — auto-generated from these docs, raw markdown, LLM-optimized.
