"""Task Runner — processes a single task through the complete state machine lifecycle.

Orchestrates: worktree setup, agent execution (implement + review),
quality gates, and terminal state resolution. All dependencies injected
via constructor for testability.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from hpnc.agents.base import ExitStatus
from hpnc.core.state_machine import TaskState, transition
from hpnc.events.base import RunResult
from hpnc.infra.errors import HpncError

if TYPE_CHECKING:
    from hpnc.agents.base import AgentExecutor
    from hpnc.events.base import TaskEventListener
    from hpnc.gates.runner import GateRunner
    from hpnc.infra.config import Config
    from hpnc.infra.git import GitWrapper
    from hpnc.infra.workspace import Workspace

__all__ = ["TaskRunner"]

logger = logging.getLogger(__name__)


class TaskRunner:
    """Processes a single task through the complete state machine lifecycle.

    Dependencies are injected via constructor for full testability.

    Args:
        executor: AgentExecutor for task implementation.
        reviewer: AgentExecutor for code review (different instance).
        gates: GateRunner for quality verification.
        listener: TaskEventListener for status persistence.
        workspace: Workspace for file operations.
        config: Project configuration.
        git: GitWrapper for branch/worktree operations.
        executor_name: Identifier for the executor agent (e.g., "opus").
        reviewer_name: Identifier for the reviewer agent (e.g., "codex").
    """

    def __init__(
        self,
        executor: AgentExecutor,
        reviewer: AgentExecutor,
        gates: GateRunner,
        listener: TaskEventListener,
        workspace: Workspace,
        config: Config,
        git: GitWrapper,
        executor_name: str = "executor",
        reviewer_name: str = "reviewer",
    ) -> None:
        self.executor = executor
        self.reviewer = reviewer
        self.gates = gates
        self.listener = listener
        self.workspace = workspace
        self.config = config
        self.git = git
        self.executor_name = executor_name
        self.reviewer_name = reviewer_name

    def run(
        self,
        task_name: str,
        story: Path,
        instructions: Path,
        worktree_base: Path,
    ) -> RunResult:
        """Execute the complete task lifecycle.

        Args:
            task_name: Task identifier (used for branch naming).
            story: Path to the story markdown file.
            instructions: Path to executor instructions file.
            worktree_base: Base directory for creating the worktree.

        Returns:
            RunResult with the final task outcome.
        """
        branch = f"night/{task_name}"
        worktree = worktree_base / task_name
        started = datetime.now(tz=UTC).isoformat()
        state = TaskState.QUEUED
        worktree_created = False

        try:
            # QUEUED -> SETUP_WORKTREE
            state = self._transition(task_name, state, TaskState.SETUP_WORKTREE)
            self.git.create_branch(branch)
            self.git.create_worktree(worktree, branch)
            worktree_created = True

            # SETUP_WORKTREE -> IMPLEMENTATION
            state = self._transition(task_name, state, TaskState.IMPLEMENTATION)
            impl_status = self._run_agent(
                task_name, self.executor, story, instructions, "implementation"
            )
            if impl_status != ExitStatus.SUCCESS:
                state = self._transition(task_name, state, TaskState.BLOCKED)
                return self._complete(
                    task_name, state, branch, started, story,
                )

            # IMPLEMENTATION -> REVIEW
            state = self._transition(task_name, state, TaskState.REVIEW)
            review_status = self._run_agent(
                task_name, self.reviewer, story, instructions, "review"
            )
            if review_status != ExitStatus.SUCCESS:
                state = self._transition(task_name, state, TaskState.BLOCKED)
                return self._complete(
                    task_name, state, branch, started, story,
                )

            # REVIEW -> GATES
            state = self._transition(task_name, state, TaskState.GATES)
            gate_results = self.gates.run_all(worktree)

            if gate_results.passed:
                state = self._transition(task_name, state, TaskState.DONE)
            else:
                state = self._transition(task_name, state, TaskState.FAILED)
                failed_gates = [
                    r.name for r in gate_results.results if not r.passed
                ]
                logger.error(
                    "Task %s: gates failed: %s", task_name, ", ".join(failed_gates)
                )

            return self._complete(task_name, state, branch, started, story)

        except HpncError:
            logger.exception("Task %s: HPNC error during lifecycle", task_name)
            if state not in {TaskState.DONE, TaskState.FAILED, TaskState.BLOCKED}:
                old_state = state
                try:
                    state = transition(state, TaskState.FAILED)
                    self.listener.on_status_change(task_name, old_state, state)
                except HpncError:
                    state = TaskState.FAILED
            try:
                return self._complete(task_name, state, branch, started, story)
            except Exception:
                logger.exception("Task %s: failed to write completion", task_name)
                return RunResult(
                    status=state, executor=self.executor_name,
                    reviewer=self.reviewer_name, branch=branch,
                    started=started, finished=datetime.now(tz=UTC).isoformat(),
                    story_source=str(story),
                )

        except Exception:
            logger.exception("Task %s: unexpected error during lifecycle", task_name)
            state = TaskState.FAILED
            try:
                return self._complete(task_name, state, branch, started, story)
            except Exception:
                logger.exception("Task %s: failed to write completion", task_name)
                return RunResult(
                    status=state, executor=self.executor_name,
                    reviewer=self.reviewer_name, branch=branch,
                    started=started, finished=datetime.now(tz=UTC).isoformat(),
                    story_source=str(story),
                )

        finally:
            if worktree_created:
                try:
                    self.git.remove_worktree(worktree)
                except (HpncError, OSError):
                    logger.warning(
                        "Task %s: failed to clean up worktree at %s",
                        task_name,
                        worktree,
                    )

    def _transition(
        self, task_name: str, current: TaskState, target: TaskState
    ) -> TaskState:
        """Transition state and fire listener.

        Args:
            task_name: Task identifier for logging.
            current: Current state.
            target: Target state.

        Returns:
            The new state.
        """
        new_state = transition(current, target)
        self.listener.on_status_change(task_name, current, new_state)
        return new_state

    def _run_agent(
        self,
        task_name: str,
        agent: AgentExecutor,
        story: Path,
        instructions: Path,
        phase: str,
    ) -> ExitStatus:
        """Run an agent and capture output.

        Args:
            task_name: Task identifier.
            agent: The agent executor to invoke.
            story: Path to the story file.
            instructions: Path to instructions file.
            phase: Phase name for progress logging.

        Returns:
            The agent's exit status.
        """
        process = agent.start(story, self.config, instructions)
        for line in agent.stream_output(process):
            self.listener.on_progress(task_name, phase, line)
        return agent.get_exit_status(process)

    def _complete(
        self,
        task_name: str,
        state: TaskState,
        branch: str,
        started: str,
        story: Path,
    ) -> RunResult:
        """Create RunResult and fire completion event.

        Args:
            task_name: Task identifier.
            state: Final task state.
            branch: Git branch name.
            started: ISO timestamp of start.
            story: Path to story file.

        Returns:
            The completed RunResult.
        """
        finished = datetime.now(tz=UTC).isoformat()
        result = RunResult(
            status=state,
            executor=self.executor_name,
            reviewer=self.reviewer_name,
            branch=branch,
            started=started,
            finished=finished,
            story_source=str(story),
        )
        self.listener.on_complete(task_name, result)
        return result
