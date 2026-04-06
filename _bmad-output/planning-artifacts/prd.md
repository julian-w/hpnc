---
stepsCompleted: [step-01-init, step-02-discovery, step-02b-vision, step-02c-executive-summary, step-03-success, step-04-journeys, step-05-domain-skipped, step-06-innovation, step-07-project-type, step-08-scoping, step-09-functional, step-10-nonfunctional, step-11-polish, step-12-complete]
inputDocuments:
  - _bmad-output/hpnc-konzept-v2.md
  - _bmad-output/brainstorming/brainstorming-session-2026-04-06-001.md
documentCounts:
  briefs: 0
  research: 0
  brainstorming: 1
  projectDocs: 0
  userProvided: 1
classification:
  projectType: cli_tool / developer_tool
  domain: developer_tooling_ai_orchestration
  complexity: medium-high
  projectContext: greenfield
workflowType: 'prd'
---

# Product Requirements Document - hpnc

**Author:** Julian
**Date:** 2026-04-06

## Executive Summary

HPNC (Human-Planned Night Crew) turns unused AI token budgets and overnight hours into reviewed, tested, merge-ready code. Developers structure and clarify work during the day using BMAD as the planning framework. At night, a crew of AI agents — currently Opus (via Claude Code) and Codex — autonomously implements fully prepared tasks in isolated Git worktrees, runs cross-model reviews, executes quality gates, and delivers results by morning.

The target user is a developer or small team already using AI coding tools and hitting their limits: the constant waiting to see if the agent goes in the right direction, the re-prompting when it doesn't, the lost focus from babysitting a process that should be autonomous. HPNC replaces this reactive workflow with a proactive one — clarify everything upfront, let it run, review results in the morning.

Locally orchestrated — all scheduling, task management, test execution, and quality gates run on the developer's machine. AI model inference is the only external dependency, accessed via cloud APIs. The architecture assumes stable CLI interfaces for supported AI agents and is designed to be extensible for future agents beyond Opus and Codex.

### What Makes This Special

Existing AI coding tools operate in one of two modes: interactive (human babysits the agent) or fire-and-forget (no quality control). HPNC occupies the gap between both: structured autonomy with a safety net.

The core insight: the problem with AI-assisted coding was never "AI can't code." It was that nobody built the orchestration and quality assurance layer around it. HPNC solves this not by improving real-time human-AI interaction, but by eliminating it — replacing it with thorough preparation and controlled autonomous execution.

Key differentiators:

- **Structured planning artifacts** — tasks enter the pipeline as stories with machine-readable frontmatter (scheduling, gates, routing) and human-readable context (requirements, acceptance criteria), not loose prompts
- **Two-layer release model** — frontmatter declares "may run" (quality gate), queue declares "should run tonight" (scheduling control)
- **Cross-model review with persistent fix-loop** — reviewer is never the executor, ensuring implementation blind spots are caught by a model that didn't write the code; up to 3 fix attempts with role swap after 2 failures
- **Morning-ready results** — every run produces a status report, reviewed branches, test results, and clear next steps; no archaeology required

HPNC is not a CI/CD pipeline, not a deployment tool, and not an IDE extension. It operates upstream of CI — preparing, implementing, and reviewing code changes that then flow through the project's existing build and deployment infrastructure.

## Project Classification

- **Project Type:** CLI Tool / Developer Tool — primary interface is the `hpnc` CLI with commands for queue management, validation, execution, and morning review
- **Domain:** Developer Tooling / AI Agent Orchestration — orchestrates AI coding agents within a structured planning and quality framework
- **Complexity:** Medium-High — state machine design, multi-agent orchestration, crash recovery, cross-platform support (Windows/Linux), API limit handling; no regulatory or compliance requirements
- **Project Context:** Greenfield — new product, no existing codebase

## Success Criteria

### User Success

- **First run success** — first night run produces at least 1 task with `done` status without manual intervention
- **Daily rhythm established** — 5 consecutive workdays with at least 1 night run each, where morning review takes less than 15 minutes
- **Trust threshold** — 3 consecutive night runs without `failed` status on correctly prepared tasks

### Business Success

- **Personal standard tool** — HPNC permanently replaces manual AI babysitting as the default workflow for implementation tasks
- Open source under MIT license; external adoption is a welcome side effect, not a primary success metric

### Technical Success

- **Gate reliability** — zero false-positive gate passes in the first 20 night runs (a gate must never report "pass" when the build or tests are actually broken)
- **Report accuracy** — no report may misrepresent a task's status; if `run.yaml` says `done`, the build and tests must actually be green
- **Crash recovery** — interrupted runs are detected, correctly marked as `interrupted`, and reported; no silent data loss
- **Cross-model review effectiveness** — Codex review catches issues that Opus implementation missed (validated qualitatively in first 10 runs)
- **Fix-loop success rate** — resolves ≥30% of review failures autonomously (post-MVP, once fix-loop is implemented)

### Measurable Outcomes

- A single task completing an end-to-end night run (queued → implementation → review → gates → done) is the MVP success milestone
- 3+ tasks per night with stable sequential processing is the MVP Complete milestone
- Reports are useful enough to make morning decisions within minutes, not hours
- Token cost per task is tracked and visible via run artifacts

## Product Scope

### Phase 1: MVP Launch

The smallest system that proves the concept: one task, one night, one result.

**Dispatcher:**
- Load and parse `night-queue.yaml`
- Validate story frontmatter (night_ready, mandatory fields)
- Start a single Task-Runner sequentially
- Generate markdown report after completion
- Persist dispatcher state

**Task-Runner:**
- State machine: queued → implementation (Opus) → review (Codex) → gates → done/failed/blocked
- AgentExecutor abstraction (3 capabilities: start agent with story+config+instructions, stream/buffer output for logging, return exit status)
- Mock-AgentExecutor built-in for testing and demos (`hpnc start --mock`)
- Quality gates: build + tests + lint
- Write `run.yaml` with task results
- Worktree setup and cleanup

**CLI (5 core commands + mock mode):**
- `hpnc init` — project setup: generate config with defaults, connectivity check (Claude Code + Codex reachable), BMAD detection
- `hpnc validate` — pre-flight check: frontmatter, blocking_questions, tests_required, worktree availability, secrets hook
- `hpnc start` — start the night run (with `--at`, `--delay`, `--dry-run`, `--mock`)
- `hpnc status` — morning review: what happened last night
- `hpnc queue add` — add a story to the night queue

**Validate scope:**
- Frontmatter mandatory fields present
- `blocking_questions` empty
- `tests_required` defined
- Git worktrees can be created
- Secrets hook active

**Pilot tasks:** small UI fixes, Storybook stories, Playwright/unit tests, small refactorings.

### Phase 2: MVP Complete

All features from the concept document Phase 4, building on Phase 1:

- Fix-loop with role swap (3 attempts, swap executor after 2)
- Codex as executor + Opus as reviewer (bidirectional routing)
- API limit detection + pause/resume
- Timeout + activity watchdog
- Protected paths post-run check
- Startup crash recovery (running → interrupted detection)
- Full run artifacts: `cost.json`, `review.md` (token tracking via CLI output parsing)
- Sequential multi-task queue processing with `depends_on` and `release_policy`
- Full CLI: `hpnc show`, `hpnc diff`, `hpnc queue remove/reorder`, `hpnc history`, `hpnc costs`, `hpnc config`
- Validate extended: dev server check, DB connection, port availability, disk space

### Phase 3: Growth

- Configurable parallelization (max 1 Opus + 1 Codex simultaneously)
- `hpnc resume` — continue blocked tasks in an interactive Claude Code session
- Token budget per task
- Scope gate (diff size, file count)
- Commit watchdog and test retry limits
- Desktop/email/push notifications
- `--json` output for all commands

### Phase 4: Vision

- TEA integration for structured requirement-to-test traceability
- AI-assisted merge conflict resolution
- HPNC as installable BMAD module
- Builder-based extensions for custom workflows
- Additional agent support beyond Opus and Codex
- Advanced dashboards and metrics

## Innovation & Novel Patterns

### Innovation Type: Novel Combination

HPNC does not introduce fundamentally new technology. The individual building blocks — AI code generation, code review automation, task queuing, Git worktree isolation, quality gates — all exist independently. The innovation is in how they are combined and orchestrated into a coherent autonomous workflow.

### What's Novel in the Combination

- **Separation of planning and execution across time** — daytime human planning (BMAD) feeds into overnight autonomous execution, creating a workflow that doesn't exist in current AI coding tools
- **Orchestration of non-deterministic executors** — unlike CI/CD systems that orchestrate deterministic processes (`npm test` yields the same result for the same input), HPNC orchestrates AI agents whose output is unpredictable. The fix-loop, role swap, and API-limit pausing are adaptation patterns for non-deterministic executors, not standard retry logic.
- **Cross-model review** — using a different AI model to review the implementing model's output; borrowed from human code review practice but applied to AI agents
- **Structured autonomy** — the middle ground between interactive AI coding (human watches) and uncontrolled generation (hope for the best); enforced through machine-readable story metadata, pre-validated tasks, and automated quality gates
- **Two-layer release model** — separating "is this task ready?" (frontmatter) from "should it run tonight?" (queue) is a scheduling pattern applied to AI agent orchestration

### Competitive Landscape

None of the existing tools solve the same problem HPNC addresses:

- **Claude Code Scheduling / Remote Triggers** — the closest competitor. Executes planned prompts on a schedule. But: no cross-model review, no fix-loop, no quality gates, no structured story input. HPNC's value over raw scheduling is the quality assurance layer around the execution.
- **Cursor / Copilot / Claude Code (interactive)** — require real-time human presence. The developer watches, corrects, re-prompts. HPNC eliminates this by shifting all clarification to the planning phase.
- **CI/CD systems** — operate post-commit. They test and deploy code but don't generate it. HPNC operates upstream of CI.
- **Devin / SWE-Agent / autonomous coding agents** — attempt full autonomy but without structured preparation, cross-model review, or the two-layer release model. They aim for general-purpose autonomy; HPNC aims for controlled, prepared autonomy.

### Validation Approach

- MVP Launch with a single task proves the end-to-end combination works technically
- **Time savings validation:** measure whether a task completed overnight would have taken significant interactive time — the value is proven when Julian says "that would have cost me 2 hours and HPNC did it while I slept"
- Phase 1 pilot tasks (safe, small tasks) validates that autonomous execution produces acceptable quality
- Progressive expansion to more complex tasks validates scaling of the approach
- If cross-model review doesn't add measurable value over self-review, the architecture still works — reviewer becomes optional

### Risk Mitigation

- If overnight execution proves unreliable: **degraded mode** — run HPNC during daytime in the background while working on other tasks, check `hpnc status` periodically instead of babysitting. Still better than interactive AI coding, even without the overnight benefit.
- If cross-model review is ineffective: switch to single-model with self-review as a degraded mode
- If BMAD integration is too rigid: stories can be written manually without BMAD; the frontmatter schema is the contract, not the tool that produces it

## CLI / Developer Tool Specific Requirements

### Project-Type Overview

HPNC is a CLI-first developer tool. All interaction happens through terminal commands. There is no GUI, no web interface, and no IDE integration planned. The CLI is the product — it must be fast, predictable, and produce readable output.

### Technology Stack

- **Language:** Python 3.12+ (chosen for developer familiarity, cross-platform support, and rich CLI ecosystem)
- **CLI Framework:** Typer or Click with Rich for formatted terminal output
- **Distribution:** pip/pipx package (`pipx install hpnc`, `pip install hpnc` as fallback)
- **Configuration:** YAML files in `_hpnc/` directory
- **State Persistence:** YAML files (dispatcher-state, run artifacts)
- **Cost Tracking:** JSON files (token usage per task)
- **Reports:** Markdown files (committed to Git)
- **Git Operations:** Thin subprocess wrapper around `git` CLI (no gitpython — avoids dependency complexity and memory leaks with intensive worktree operations)
- **Parallelization Strategy:** Task-Runners as separate processes (not threads), communication via state files (run.yaml). Sequential in MVP, architecture supports parallel from day one.

### Command Structure

```
hpnc
├── init          # Project setup, config generation, connectivity check
├── validate      # Pre-flight check before night run
├── start         # Start night run (--at, --delay, --dry-run)
├── status        # Morning review — what happened last night
├── show <task>   # Detailed task view (MVP Complete)
├── diff <task>   # Code changes for a task (MVP Complete)
├── queue
│   ├── add       # Add story to night queue
│   ├── remove    # Remove story from queue (MVP Complete)
│   └── reorder   # Change queue order (MVP Complete)
├── history       # Past runs overview (MVP Complete)
├── costs         # Token usage over time (MVP Complete)
└── config        # View/edit HPNC configuration (MVP Complete)
```

### Project Root Discovery

HPNC locates the project root by searching upward from the current working directory for `_hpnc/config.yaml`, analogous to how Git searches for `.git/`. All `hpnc` commands work from any subdirectory within the project.

### Exit Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 0 | Success | Command completed successfully |
| 1 | Error | Task failed, validation error, general failure |
| 2 | Blocked | Task needs human input, cannot proceed |
| 3 | Interrupted | Crash, timeout, unexpected termination |
| 4 | Config error | Missing config, invalid YAML, bad setup |
| 5 | Connectivity error | Claude Code or Codex CLI not reachable |

Exit codes enable scripting: `hpnc validate && hpnc start`.

### Output Formats

- **Terminal output:** Rich-formatted tables, colored status indicators, structured reports
- **Persisted artifacts:** YAML (state, run data), JSON (costs), Markdown (reports, reviews)
- **All artifacts are Git-committable** — plain text, diffable, mergeable
- **Machine-readable output:** `--json` flag for scripting (post-MVP)

### Configuration Schema

```yaml
# _hpnc/config.yaml
project_name: "my-project"
defaults:
  merge_target: develop
  executor: auto
  reviewer: opposite
  timeout: 30m
  max_fix_attempts: 3
  swap_executor_after: 2
  max_review_rounds: 4
schedule:
  start: "23:00"
  post_run_checks: true
parallelization:
  max_parallel: 1
logging:
  dispatcher: normal
  agent_output: truncated
  max_agent_log_lines: 500
protected_paths:
  - _hpnc/
  - _bmad/
  - .claude/
known_resources:
  - db-migrations
  - api-definitions
```

### Shell Completion

- Tab completion for bash, zsh, and fish (auto-generated by Typer/Click)
- Completes command names, subcommands, and flags
- Completes story file paths for `hpnc queue add`
- MVP Launch scope — completion significantly improves daily CLI workflow

### Connectivity Check (`hpnc init`)

- Verify Claude Code CLI is installed and reachable (version check via subprocess)
- Verify Codex CLI is installed and reachable (version check via subprocess)
- Detect existing BMAD configuration in project
- Generate `_hpnc/config.yaml` with sensible defaults
- Connectivity check is re-runnable and also used by `hpnc validate`

### Installation & Setup

```bash
pipx install hpnc          # Install globally (recommended)
pip install hpnc            # Alternative
cd my-project
hpnc init                   # Generate config, check connectivity
hpnc validate               # Verify setup
```

Prerequisites:
- Python 3.12+
- Git
- Claude Code CLI installed and authenticated
- Codex CLI installed and authenticated

### Documentation

Three documentation layers — see FR80-FR84 for full requirements:
- **CLI `--help`** — immediate terminal reference (auto-generated by Typer/Click)
- **MkDocs site** — bilingual (de/en), Material Design, full concept and configuration reference
- **`HPNC.md`** — LLM-optimized context file generated from MkDocs sources, loadable in any agent session

### Implementation Considerations

- **Cross-platform:** Windows and Linux primary targets, Mac perspective. Use `pathlib` for all path operations, avoid shell-specific assumptions.
- **Process management:** Subprocess calls for Claude Code and Codex CLIs via AgentExecutor abstraction
- **Lazy imports:** Load heavy dependencies only when the specific subcommand needs them, keeping CLI startup fast
- **File locking:** Required for state files when parallelization is added (post-MVP)
- **Optional native compilation:** Nuitka can compile to native executable for faster startup if needed (not MVP)

## User Journeys

### Journey 0: First Time Setup — "Das erste Mal"

**Julian** has just installed HPNC. He has an existing web application project with BMAD already configured. He's curious but skeptical — will this actually work?

**Opening Scene:** Julian opens the terminal in his project root. He has Claude Code and Codex installed, a BMAD-structured project, but no HPNC configuration yet.

**Rising Action:**
- `hpnc init` — HPNC creates `_hpnc/config.yaml` with sensible defaults (merge target: develop, timeout: 30m, sequential execution). It runs a connectivity check: Claude Code CLI reachable, Codex CLI reachable. It detects the existing BMAD setup and confirms compatibility.
- Julian reviews the generated config. Defaults are reasonable — he changes `merge_target` to `main` for his project.
- He picks the simplest possible task for the first run: adding a missing unit test for an existing utility function. He writes the story with BMAD, fills in the night-ready frontmatter, and makes sure `blocking_questions` is empty and `tests_required` is defined.
- `hpnc queue add stories/add-utils-test.md`
- `hpnc validate` — first validation ever. Green. The relief is real.

**Climax:** `hpnc start` — no scheduling, no delay, just "run it now and let me watch the first time." Julian stays at his desk for this one. He wants to see what happens.

**Resolution:** 18 minutes later, status: `done`. The test file exists, it passes, the review found no issues. Julian runs `hpnc status`, reads the report, checks the diff. It's clean. The first night run wasn't at night — but it proved the system works. Tomorrow, he'll schedule it for real.

**Reveals requirements for:** `hpnc init` command (config generation, connectivity check, BMAD detection), sensible defaults, first-run experience, immediate execution mode.

---

### Journey 1: The Evening Setup — "Alles klar für die Nacht"

**Julian** has spent the day planning with BMAD. Two stories are fully prepared: a login form validation fix and a new Storybook story for the button component. Both have acceptance criteria, test plans, and clear "done" definitions.

**Opening Scene:** It's 6 PM. Julian opens the terminal. He's done thinking for today — now he wants to hand off the work.

**Rising Action:**
- `hpnc queue add stories/login-validation.md` — adds the first story
- `hpnc queue add stories/button-stories.md` — adds the second
- `hpnc validate` — the pre-flight check runs. Frontmatter complete, no blocking questions, tests defined, worktrees available, secrets hook active. Green across the board.

**The trust moment:** This is where Julian decides to let go. Validate isn't just a technical check — it's the seatbelt click. Green means: you can close the laptop. Everything that needed to be clarified, is clarified. Everything that needed to be defined, is defined. The agents won't need you tonight.

**Climax:** `hpnc start --at 23:00` — scheduled. Julian closes the laptop and goes home.

**Variant — Validate fails:**
Julian runs `hpnc validate` and gets a warning: `button-stories.md: blocking_questions is not empty — "Which ButtonGroup variant should be the default?"` He forgot to resolve that question. He opens the story, makes the decision, clears the blocking question, re-runs validate. Green. Now he can start.

**Resolution:** The system is armed. Julian's workday is over, but his productivity isn't.

**Reveals requirements for:** queue management CLI, frontmatter validation engine, scheduling system, pre-flight checks, clear validate error messages with actionable guidance.

---

### Journey 2: The Morning Harvest — "Was hat die Nacht gebracht?"

**Opening Scene:** 8 AM. Coffee in hand, Julian opens the laptop. The question isn't "did something happen?" — it's "what got done?"

**Rising Action:**
- `hpnc status` — the morning report appears:

```
HPNC Night Run — 2026-04-15 Report #001
2 tasks executed: 1 done, 1 blocked

| # | Task              | Executor | Reviewer | Status  | Duration |
|---|-------------------|----------|----------|---------|----------|
| 1 | login-validation  | opus     | codex    | done    | 24min    |
| 2 | button-stories    | opus     | codex    | blocked | 18min    |
```

- `hpnc show login-validation` — review summary: Codex found no blocking issues, all gates green, branch `night/login-validation` ready to merge.
- `hpnc diff login-validation` — Julian scans the changes. Clean. Tests cover the acceptance criteria. He merges.

**Climax:** The login validation task — which would have taken an interactive AI session of 30+ minutes with constant supervision — was done while Julian slept. Code reviewed by a different model, tested, gate-checked, merge-ready. This is the paradigm shift: for the first time, code was written *without him being present*. Not generated-and-hope-for-the-best, but planned, executed, reviewed, and verified.

- `hpnc show button-stories` — Status: blocked. Reason and recommended next action: "Component ButtonGroup not found at expected path `src/components/ButtonGroup.tsx`. → Recommend: create ButtonGroup component first, then re-queue this story."

**Resolution:** Julian merges one branch, reads one blocker with a clear next step, and knows exactly what to do. Total morning review time: 8 minutes. The night worked for him.

**Reveals requirements for:** status report generation, show/diff commands, clear blocker messaging with recommended next actions, merge-ready branch delivery.

---

### Journey 3: The Daytime Planner — "Morgen soll die Nacht wieder arbeiten"

**Opening Scene:** 10 AM. Julian's morning review is done. One task merged, one blocked. Now he shifts into planning mode.

**Rising Action:**
- The blocked button-stories task needs a ButtonGroup component first. Julian opens BMAD and creates a new story for the component — acceptance criteria, test plan, UI specifications.
- He marks the story `night_ready: true` once everything is clarified.
- He also prepares two more stories from the current epic that have been waiting for clarification — a form refactoring and an API endpoint test.
- Each story gets its frontmatter: executor, reviewer, risk level, touches, tests_required.

**Climax:** By afternoon, Julian has 3 new stories night-ready and the fixed button-stories ready for re-queue. He didn't write a single line of implementation code today. His entire day was spent thinking, clarifying, and structuring.

**Resolution:** Julian queues 4 stories for tonight. Tomorrow morning, he expects results. The cycle continues — plan by day, harvest by morning.

**Reveals requirements for:** BMAD integration, story format with night-ready frontmatter, queue management, re-queuing blocked tasks.

---

### Journey 4: The Bad Morning — "Letzte Nacht lief nicht gut"

**Opening Scene:** 8 AM. Julian runs `hpnc status`. The report looks different today:

```
HPNC Night Run — 2026-04-18 Report #003
3 tasks executed: 0 done, 1 blocked, 1 failed, 1 interrupted

| # | Task           | Executor | Status      | Duration |
|---|----------------|----------|-------------|----------|
| 1 | nav-refactor   | opus     | blocked     | 30min    |
| 2 | user-api       | opus     | failed      | 15min    |
| 3 | form-cleanup   | opus     | interrupted | 8min     |
```

**Rising Action:**
- `hpnc show nav-refactor` — blocked after 3 fix rounds including role swap. Recommended next action: "Refactoring scope significantly larger than story describes. Touches 12 files across 3 modules. → Recommend: split into 3 smaller stories covering (1) nav-header extraction, (2) nav-sidebar refactor, (3) nav-mobile adaptation."
- `hpnc show user-api` — failed. Build broken: a dependency updated overnight and introduced a breaking change. Gates caught it — no code was merged. Recommended next action: "→ Pin dependency version in package.json, then re-queue."
- `hpnc show form-cleanup` — interrupted. Two scenarios happened: the dispatcher detected that the task-runner process died unexpectedly (Windows update triggered a restart at 03:47). Startup recovery correctly marked the task as `interrupted` and preserved the dispatcher state. Recommended next action: "→ Task was progressing normally before interruption. Safe to re-queue as-is."

**Climax:** Zero tasks merged. But Julian isn't frustrated — he's *informed*. Every failure has a clear explanation, a clear status, and a clear recommended next action. No silent corruption, no half-finished merges, no mystery state.

**Resolution:**
- nav-refactor: Julian splits the story into 3 smaller ones using BMAD. Re-queues for tomorrow.
- user-api: Julian pins the dependency version and re-queues.
- form-cleanup: Julian re-queues as-is — the task itself was fine, just unlucky timing.

Total damage assessment: 15 minutes. Total data loss: zero.

**Reveals requirements for:** detailed failure reporting with recommended next actions, scope detection, crash recovery (startup recovery for dead processes), clear status explanations, safe failure modes, actionable report output.

---

### Journey Requirements Summary

| Capability Area | Revealed By Journey |
|----------------|-------------------|
| `hpnc init` (config, connectivity, BMAD detection) | First Time Setup |
| Sensible defaults and first-run experience | First Time Setup |
| Queue management CLI | Evening Setup |
| Frontmatter validation engine | Evening Setup |
| Clear validate errors with actionable guidance | Evening Setup |
| Scheduling system (--at, --delay) | Evening Setup |
| Trust-building pre-flight checks | Evening Setup |
| Status report generation | Morning Harvest |
| Show/diff commands | Morning Harvest |
| Blocker messaging with recommended next actions | Morning Harvest, Bad Morning |
| Merge-ready branch delivery | Morning Harvest |
| BMAD integration (story format) | Daytime Planner |
| Night-ready frontmatter schema | Daytime Planner |
| Re-queuing mechanism | Daytime Planner |
| Detailed failure reporting with next actions | Bad Morning |
| Scope detection (agent stops on oversize) | Bad Morning |
| Crash recovery (startup recovery) | Bad Morning |
| Safe failure modes (no silent corruption) | Bad Morning |

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Problem-Solving MVP — prove that one task can be autonomously executed, reviewed, and delivered overnight. Not feature-complete, not a platform — a proof that the plan-by-day, harvest-by-morning workflow works end-to-end.

**Resource Requirements:** Solo developer (Julian). All implementation either done manually or via HPNC itself once bootstrapped. No team dependencies, no external stakeholders.

### Phase Definitions (Canonical Reference)

All sections in this PRD use these phase names consistently:

| Phase | Name | Scope | Success Milestone |
|-------|------|-------|-------------------|
| 1 | MVP Launch | One task, one night, one result | First successful autonomous night run |
| 2 | MVP Complete | Full concept document Phase 4 | Stable daily use with multiple tasks |
| 3 | Growth | Parallelization, resume, notifications | Scaling to complex multi-task nights |
| 4 | Vision | TEA, BMAD module, AI merge resolution | Full ecosystem integration |

### AgentExecutor Architecture (Critical Path)

The AgentExecutor abstraction is the single most important interface in the project. If it is clean, tests are cheap, new agents are trivial to add, and mocking works. If it is poor, everything becomes expensive.

**Interface (3 capabilities only):**
1. Start agent with story + config + executor instructions
2. Stream or buffer output (for logging)
3. Return exit status (success / failure / timeout)

No token parsing in Phase 1 (that's Phase 2 `cost.json`). No output format parsing (the agent writes directly into the worktree). The AgentExecutor is a process wrapper, nothing more.

**Mock-AgentExecutor:** Ships with HPNC. Simulates agent behavior (waits, writes dummy files, returns configurable status). Enables:
- Full dispatcher + task-runner + report chain testing without spending tokens
- `hpnc start --mock` for demos and dry-runs
- New users can try HPNC before committing to AI provider accounts

### Test Strategy

Testing an AI orchestration tool is inherently expensive because real test runs consume API tokens and time. The strategy minimizes token usage through layered testing:

**Layer 1: Unit Tests (zero tokens, zero API calls) — ~60% of codebase**
- State machine transitions: every path through queued → implementation → review → gates → done/failed/blocked
- Config parsing and validation engine: YAML loading, mandatory field checks, exit codes
- Queue logic: `depends_on` resolution, `release_policy`, ordering
- Report generation: status data in, markdown report out
- Project root discovery, shell completion

**Layer 2: Integration Tests with Mock-AgentExecutor (zero tokens)**
- Mock delivers predefined results: success, failure, timeout, blocked
- Tests the entire Task-Runner lifecycle without a single API call
- Fix-loop, role swap, crash recovery — all testable with mocks
- Dispatcher → Task-Runner → Report chain fully exercisable

**Layer 3: Record/Replay (tokens spent once, then free)**
- Record real agent interactions (request + response) once
- Replay in subsequent test runs
- Periodically refresh recordings when CLI output format changes

**Layer 4: E2E Smoke Tests (expensive, run sparingly)**
- Maximum 3-5 tests with real agents
- Only for: "can HPNC start Claude Code and parse its output?"
- Run before releases, not on every commit

**Key insight:** If the AgentExecutor abstraction is clean, 90%+ of tests are token-free. The testing risk reduces to "is the abstraction good enough?" — an architecture question, not a testing question.

### Risk Mitigation Strategy

**Technical Risks:**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Claude Code / Codex CLI interface changes | High — breaks AgentExecutor | Medium | Thin abstraction layer isolates CLI-specific behavior. Version-pin supported CLI versions. Token tracking (`cost.json`) deferred to Phase 2 — if CLI output format changes, only tracking breaks, not core function. |
| Agent produces subtly wrong code that passes gates | High — erodes trust | Medium | Cross-model review is the primary defense. Phase 1 uses only safe, small tasks to build confidence before expanding scope. |
| Worktree management edge cases (locks, permissions, long paths) | Medium | Medium | Windows `core.longpaths = true`, `.gitattributes`, short task names. Test on Windows early. |

**Testing Risk (primary concern):**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Testing costs many tokens and takes long time | High — slows development | High | 4-layer test strategy (see above). Mock-AgentExecutor enables 90%+ token-free testing. E2E tests only before releases. |

**Market Risks:**
- Not applicable — personal tool, open source under MIT. Success = Julian uses it daily.

**Resource Risks:**
- Solo developer project. MVP Launch is scoped small enough to be achievable in a focused sprint. Each phase delivers standalone value — Phase 1 is useful even if later phases are never built.

## Functional Requirements

### Project Setup & Configuration

- **FR1:** Developer can initialize a new HPNC project in an existing repository (`hpnc init`)
- **FR2:** System can detect and verify connectivity to Claude Code CLI
- **FR3:** System can detect and verify connectivity to Codex CLI
- **FR4:** System can detect existing BMAD configuration in the project
- **FR5:** System can generate a default `_hpnc/config.yaml` with sensible defaults
- **FR6:** Developer can modify project configuration via YAML file
- **FR7:** System can locate the project root by searching upward for `_hpnc/config.yaml`
- **FR8:** System provides shell completion for commands, subcommands, flags, and story file paths (bash/zsh/fish)

### Story & Queue Management

- **FR9:** Developer can add a story file to the night queue (`hpnc queue add`)
- **FR10:** Developer can remove a story from the night queue (Phase 2)
- **FR11:** Developer can reorder stories in the night queue (Phase 2)
- **FR12:** System can read and parse `night-queue.yaml` including task groups and priorities
- **FR13:** System can parse story frontmatter to extract night-ready metadata (executor, reviewer, risk, tests_required, touches, etc.)
- **FR14:** System can evaluate `depends_on` relationships between tasks (Phase 2)
- **FR15:** System can evaluate `release_policy` for task groups (Phase 2)
- **FR16:** System can define and expose the night-ready frontmatter schema as a machine-readable specification
- **FR17:** System can consume any story file that conforms to the night-ready frontmatter schema, regardless of how it was created

### Validation & Pre-flight

- **FR18:** Developer can run a pre-flight validation check (`hpnc validate`)
- **FR19:** System can verify that all queued stories have `night_ready: true`
- **FR20:** System can verify that all mandatory frontmatter fields are present
- **FR21:** System can verify that `blocking_questions` is empty for each story
- **FR22:** System can verify that `tests_required` is defined for each story
- **FR23:** System can verify that Git worktrees can be created
- **FR24:** System can verify that a secrets hook (git-secrets/gitleaks) is active
- **FR25:** System can report validation failures with actionable guidance
- **FR26:** System can verify dev server, DB connection, port availability, disk space (Phase 2)

### Night Run Execution

- **FR27:** Developer can start a night run immediately (`hpnc start`)
- **FR28:** Developer can schedule a night run for a specific time (`hpnc start --at`)
- **FR29:** Developer can schedule a night run with a delay (`hpnc start --delay`)
- **FR30:** Developer can simulate a night run without executing agents (`hpnc start --dry-run`)
- **FR31:** Developer can run the night queue with mock agents (`hpnc start --mock`)
- **FR32:** System can process queued tasks sequentially
- **FR33:** System can persist dispatcher state after each task completion
- **FR34:** System can clean up completed tasks from the queue

### Task Lifecycle & State Management

- **FR35:** System can create a named branch (`night/<task-name>`) and manage worktree lifecycle (create, cleanup, handle orphaned worktrees)
- **FR36:** System can transition tasks through the state machine: queued → implementation → review → gates → terminal status
- **FR37:** System can invoke an AI agent for task implementation via AgentExecutor
- **FR38:** System can invoke a different AI agent for task review via AgentExecutor
- **FR39:** System can transition tasks to `done` when all gates pass
- **FR40:** System can transition tasks to `failed` when gates fail
- **FR41:** System can transition tasks to `blocked` when the agent cannot proceed without human input
- **FR42:** System can mark tasks as `proposal` when implementation is complete but human review is required before merge (Phase 2)
- **FR43:** System can mark tasks as `interrupted` when the process terminates unexpectedly (Phase 2)
- **FR44:** System can execute a fix-loop with configurable retry attempts (Phase 2)
- **FR45:** System can swap the executor role after configurable failed attempts (Phase 2)
- **FR46:** System can detect and handle API rate limits by pausing and resuming (Phase 2)
- **FR47:** System can enforce task timeout and detect agent inactivity (Phase 2)
- **FR48:** System can detect interrupted runs on startup and mark them correctly (Phase 2)
- **FR49:** System can clean up worktrees after task completion
- **FR50:** System can write `run.yaml` with mandatory fields: status, executor, reviewer, branch, started, finished, files_changed, story_source
- **FR51:** System can write `cost.json` with token usage per task (Phase 2)
- **FR52:** System can write `review.md` with structured review findings (Phase 2)

### Quality Assurance & Gates

- **FR53:** System can execute build verification as a quality gate
- **FR54:** System can execute test suite as a quality gate
- **FR55:** System can execute linting as a quality gate
- **FR56:** System can verify that protected paths were not modified (Phase 2)
- **FR57:** System can verify that no secrets were committed (via pre-commit hook)
- **FR58:** System can auto-merge task branch into target branch when all gates pass and merge_policy is `done` (Phase 2)

### Reporting & Morning Review

- **FR59:** Developer can view a summary of the last night run (`hpnc status`)
- **FR60:** System can generate a markdown report with task results, durations, and statuses
- **FR61:** System can display blocked tasks with recommended next actions
- **FR62:** System can display failed tasks with clear failure reasons
- **FR63:** Developer can view detailed information for a specific task (`hpnc show`) (Phase 2)
- **FR64:** Developer can view code changes for a specific task (`hpnc diff`) (Phase 2)
- **FR65:** Developer can view historical run data (`hpnc history`) (Phase 2)
- **FR66:** Developer can view token cost data over time (`hpnc costs`) (Phase 2)
- **FR67:** System can commit run artifacts into the task branch
- **FR68:** Developer can view and modify HPNC configuration via CLI (`hpnc config`) (Phase 2)

### Agent Orchestration

- **FR69:** System can start an AI agent with story file, project config, and executor instructions
- **FR70:** System can stream or buffer agent output for logging
- **FR71:** System can capture agent exit status (success/failure/timeout)
- **FR72:** System can route tasks to specific agents based on story frontmatter (`executor` field)
- **FR73:** System can route reviews to specific agents based on story frontmatter (`reviewer` field)
- **FR74:** Developer can configure mock agent responses (status, delay, simulated file changes) for testing
- **FR75:** System provides an AgentExecutor interface that supports adding new agent types

### Logging & Observability

- **FR76:** System can log dispatcher activities at configurable verbosity levels (minimal, normal, verbose)
- **FR77:** System can capture and store agent output (full, truncated, or none, configurable per config)

### BMAD Integration

- **FR78:** BMad Builder can generate night-ready story templates based on the HPNC frontmatter schema (Phase 2)
- **FR79:** BMad Builder can validate stories against the night-ready schema before marking them ready (Phase 2)

### Documentation

- **FR80:** System provides a MkDocs documentation site with Material Design theme, bilingual (German and English)
- **FR81:** System provides built-in CLI help (`--help`) for all commands with usage examples (auto-generated by Typer/Click)
- **FR82:** System provides an LLM-optimized context file (`HPNC.md`) generated from MkDocs sources, containing system concepts, status classes, CLI reference, and frontmatter schema — loadable in any agent session for HPNC-aware assistance
- **FR83:** System provides a separate project-specific `executor-instructions.md` (manually maintained per project) with strict rules for autonomous night execution
- **FR84:** Documentation site covers: getting started, concepts (night-policy, story format, two-layer release, state machine), CLI reference, configuration reference, frontmatter schema, and troubleshooting

### Human Review Workflow (Phase 2)

- **FR85:** Developer can configure a task's `merge_policy` as `proposal` to require human review before merge (Phase 2)
- **FR86:** System can generate human review instructions for `proposal`-status tasks, including what to test and what to check (Phase 2)
- **FR87:** Developer can approve or reject a `proposal`-status task via CLI after manual review (`hpnc approve <task>`, `hpnc reject <task>`) (Phase 2)
- **FR88:** System merges a `proposal` task only after explicit human approval — never automatically (Phase 2)
- **FR89:** Morning report clearly surfaces `proposal` tasks that await human review, with review instructions and branch name for manual testing (Phase 2)

## Non-Functional Requirements

### Reliability

HPNC runs unsupervised for hours. Silent failures are unacceptable — every anomaly must be visible in the morning.

- **NFR1:** System must never silently discard, ignore, or fail to report a task error. Every failure, timeout, crash, and unexpected state must appear in the morning report.
- **NFR2:** System must persist dispatcher state to disk after every state transition. A crash at any point must not lose information about completed or in-progress tasks.
- **NFR3:** System must detect its own unexpected termination on next startup and mark affected tasks as `interrupted` with the last known state.
- **NFR4:** System must not corrupt Git repository state under any failure condition. If a worktree operation fails mid-way, the main branch and other worktrees must remain unaffected. `git fsck` on the main repository must pass after every night run.
- **NFR5:** System must log all significant events (task start, status transitions, gate results, errors) with timestamps, even at `minimal` logging verbosity.
- **NFR6:** System must gracefully handle agent process crashes (non-zero exit, segfault, hung process) without leaving orphaned worktrees or locked files.

### Data Integrity

No silent data loss. No half-finished merges. No corrupted state.

- **NFR7:** System must never auto-merge a branch unless all quality gates have verifiably passed. A false-positive gate pass is a critical bug.
- **NFR8:** Run artifacts (`run.yaml`, reports) must accurately reflect the actual task outcome. A report claiming `done` when the build is red is a critical bug.
- **NFR9:** System must not modify files outside the task's worktree during execution. The main branch, other worktrees, and `_hpnc/` configuration must remain untouched by agents.
- **NFR10:** Queue cleanup must only remove tasks that have reached a terminal state (`done`, `failed`, `blocked`, `interrupted`). A task in `running` state must never be silently removed.
- **NFR11:** All persisted files (dispatcher state, run.yaml, queue file) must use atomic writes — write to temp file, then rename. A crash during write must not produce a corrupt file.

### Recoverability

After any failure, the system must be usable again without manual cleanup.

- **NFR12:** After a crash, the next `hpnc start` must work without manual intervention. Orphaned worktrees, stale state files, and incomplete queue entries must be automatically detected and cleaned up.
- **NFR13:** Recovery must preserve all information about completed tasks. Only the crashed task's state may be uncertain — and it must be clearly marked as `interrupted`.

### Idempotency

- **NFR14:** Running `hpnc start` while a dispatcher is already running must be detected and rejected with a clear error — not start a second parallel dispatcher.
- **NFR15:** `hpnc validate` must be a pure read-only operation that never modifies state.
- **NFR16:** `hpnc init` in an already-initialized project must not overwrite existing configuration. It must detect the existing setup and report it.

### Graceful Degradation

- **NFR17:** If any required agent (Claude Code or Codex) is not reachable, `hpnc validate` must report the failure clearly and `hpnc start` must refuse to run. No degraded execution without review in Phase 1 — quality over throughput.

### Security

- **NFR18:** Agents must not have write access to protected paths (`_hpnc/`, `_bmad/`, `.claude/`). Violations must be detected post-run and cause task failure.
- **NFR19:** System must verify that a secrets pre-commit hook is active before starting any night run. No run without secret protection.
- **NFR20:** Agent credentials (API keys, tokens) must never be logged, stored in run artifacts, or committed to Git.

### Performance

- **NFR21:** CLI commands (`status`, `validate`, `queue add`) must complete within 2 seconds under normal conditions (excluding agent execution time).
- **NFR22:** Dispatcher overhead (queue parsing, validation, report generation) must add less than 60 seconds to a night run, regardless of queue size.
- **NFR23:** State file writes must complete within 1 second to minimize the window for crash-induced data loss.

### Error Messages

- **NFR24:** Every error message must contain three elements: (1) what happened, (2) why it happened (if known), (3) what the user can do about it. This applies to CLI errors, validate warnings, and report entries equally.

### Integration

- **NFR25:** System must work with any Git repository that supports worktrees (Git 2.20+).
- **NFR26:** AgentExecutor must isolate all CLI-specific behavior behind the abstraction. A change in Claude Code CLI output format must not require changes outside the ClaudeCodeExecutor class.
- **NFR27:** System must not depend on specific BMAD version or features. The night-ready frontmatter schema is the contract — any tool that produces conformant story files is supported.

### Cross-Platform

- **NFR28:** Phase 1 must run reliably on Windows 10/11. Linux support is targeted for Phase 2+.
- **NFR29:** All file paths must use platform-independent handling (`pathlib`). No hardcoded path separators.
- **NFR30:** System must handle Windows-specific constraints: long paths (`core.longpaths`), file locking behavior, case-insensitive filesystems.

### Documentation Quality

- **NFR31:** Documentation must be kept in sync with implementation. Generated documentation (CLI help, `HPNC.md`) must be regenerated as part of the build/release process.
- **NFR32:** `HPNC.md` must be regenerable from MkDocs sources via a single command — no manual curation of the LLM context file.
