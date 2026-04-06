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
