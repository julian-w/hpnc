"""Entry point for `python -m hpnc.core.task_runner`.

Reads a task-spec.yaml and runs the task through the complete lifecycle.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from hpnc.agents.mock import MockAgentExecutor
from hpnc.core.task_runner import TaskRunner
from hpnc.events.file_listener import FileEventListener
from hpnc.gates.build import BuildGate
from hpnc.gates.lint import LintGate
from hpnc.gates.runner import GateRunner
from hpnc.gates.tests import TestGate
from hpnc.infra.config import Config
from hpnc.infra.git import GitWrapper
from hpnc.infra.workspace import Workspace


def main() -> None:
    """Parse task-spec.yaml and run the task lifecycle."""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m hpnc.core <task-spec.yaml>\n")
        sys.exit(1)

    spec_path = Path(sys.argv[1])
    with spec_path.open() as f:
        spec = yaml.safe_load(f)

    project_root = Path(spec.get("config", ".")).parent.parent
    workspace = Workspace(root=project_root)
    config = Config(
        project_name=spec.get("project_name", "hpnc"),
        project_root=project_root,
    )
    git = GitWrapper(repo_root=project_root)

    run_dir = Path(spec.get("run_dir", "_hpnc/runs/default"))
    listener = FileEventListener(run_dir=run_dir, workspace=workspace)

    executor = MockAgentExecutor()
    reviewer = MockAgentExecutor()

    gates = GateRunner(gates=[BuildGate(), TestGate(), LintGate()])

    runner = TaskRunner(
        executor=executor,
        reviewer=reviewer,
        gates=gates,
        listener=listener,
        workspace=workspace,
        config=config,
        git=git,
    )

    story = Path(spec["story"])
    instructions = Path(spec.get("instructions", "_hpnc/executor-instructions.md"))
    worktree_base = Path(spec.get("worktree_base", "/tmp/hpnc-night"))
    task_name = spec.get("task_name", story.stem)

    result = runner.run(
        task_name=task_name,
        story=story,
        instructions=instructions,
        worktree_base=worktree_base,
    )

    exit_code = 0 if result.status.value == "done" else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
