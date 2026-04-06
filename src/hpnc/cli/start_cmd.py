"""hpnc start — night run execution command (FR27-FR31).

Supports immediate start, --at, --delay, --dry-run, --mock.
"""

from __future__ import annotations

import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from hpnc.agents.base import AgentExecutor
from hpnc.agents.mock import MockAgentExecutor
from hpnc.agents.routing import get_executor
from hpnc.core.dispatcher import Dispatcher
from hpnc.core.queue_manager import QueueManager
from hpnc.gates.build import BuildGate
from hpnc.gates.lint import LintGate
from hpnc.gates.runner import GateRunner
from hpnc.gates.tests import TestGate
from hpnc.infra.config import CONFIG_DIR, ConfigLoader
from hpnc.infra.errors import HpncError
from hpnc.infra.git import GitWrapper
from hpnc.infra.process_lock import ProcessLock
from hpnc.infra.workspace import Workspace


def _parse_delay(delay_str: str) -> float:
    """Parse a delay string like '30m', '2h', '90s' into seconds.

    Args:
        delay_str: Duration string with suffix (s/m/h).

    Returns:
        Duration in seconds.

    Raises:
        ValueError: If the delay is invalid or negative.
    """
    delay_str = delay_str.strip().lower()
    if delay_str.endswith("h"):
        result = float(delay_str[:-1]) * 3600
    elif delay_str.endswith("m"):
        result = float(delay_str[:-1]) * 60
    elif delay_str.endswith("s"):
        result = float(delay_str[:-1])
    else:
        result = float(delay_str)
    if result < 0:
        msg = f"Delay must be non-negative, got: {delay_str}"
        raise ValueError(msg)
    return result


def _wait_until(target_time: str, console: Console) -> None:
    """Wait until a target time (HH:MM format, local time).

    Handles sleep/hibernate by checking actual time on wake.

    Args:
        target_time: Time string in HH:MM format.
        console: Rich console for output.

    Raises:
        ValueError: If the time format is invalid.
    """
    parts = target_time.split(":")
    if len(parts) != 2:
        msg = f"Invalid time format: '{target_time}'. Expected HH:MM"
        raise ValueError(msg)
    hour, minute = int(parts[0]), int(parts[1])
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        msg = f"Invalid time: {hour:02d}:{minute:02d}"
        raise ValueError(msg)

    now = datetime.now()  # local time — user means local when typing "23:00"
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)

    delay = (target - now).total_seconds()
    if delay <= 0:
        return

    console.print(f"  Scheduled for {target_time} — waiting {delay:.0f}s...")
    time.sleep(delay)

    # Handle hibernate/sleep time jumps — re-check after wake
    actual = datetime.now()
    if actual < target:
        remaining = (target - actual).total_seconds()
        if remaining > 0:
            time.sleep(remaining)


def start(
    at: Annotated[str | None, typer.Option(help="Schedule start time (e.g. 23:00)")] = None,
    delay: Annotated[str | None, typer.Option(help="Delay before start (e.g. 30m)")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Simulate without executing")] = False,
    mock: Annotated[bool, typer.Option("--mock", help="Use mock agents")] = False,
) -> None:
    """Start a night run."""
    console = Console()

    try:
        # Validate mutually exclusive scheduling options
        if at is not None and delay is not None:
            console.print("[red]✗[/red] Cannot use both --at and --delay")
            raise typer.Exit(code=1)

        loader = ConfigLoader()
        root = loader.find_root()
        config = loader.load(root)
        workspace = Workspace(root=root)

        # Dry run — skip scheduling, just show what would happen
        if dry_run:
            queue_path = root / CONFIG_DIR / "night-queue.yaml"
            qm = QueueManager(workspace=workspace, queue_path=queue_path)
            tasks = qm.list_tasks()
            console.print(f"\n[bold]Dry run[/bold] — {len(tasks)} task(s) would be processed:")
            for t in tasks:
                console.print(f"  - {Path(t.get('story', '')).name}")
            console.print("\nNo agents executed, no state modified.")
            raise typer.Exit(code=0)

        # Scheduling (only for non-dry-run)
        if at is not None:
            _wait_until(at, console)
        elif delay is not None:
            seconds = _parse_delay(delay)
            console.print(f"  Waiting {seconds:.0f}s before starting...")
            time.sleep(seconds)

        # Build dispatcher
        git = GitWrapper(repo_root=root)
        queue_path = root / CONFIG_DIR / "night-queue.yaml"
        qm = QueueManager(workspace=workspace, queue_path=queue_path)
        lock = ProcessLock(lock_path=root / CONFIG_DIR / ".dispatcher.lock")

        executor: AgentExecutor
        reviewer: AgentExecutor
        if mock:
            executor = MockAgentExecutor()
            reviewer = MockAgentExecutor()
        else:
            executor = get_executor(config.executor)
            reviewer = get_executor(config.reviewer)
            # Pre-flight: verify agents can authenticate and work (NFR17)
            from hpnc.agents.claude_code import ClaudeCodeExecutor
            from hpnc.agents.codex import CodexExecutor

            console.print("\n[bold]Pre-flight agent check...[/bold]")
            preflight_dir = root / "_hpnc" / ".preflight"
            preflight_dir.mkdir(parents=True, exist_ok=True)
            subprocess.run(
                ["git", "init"], cwd=str(preflight_dir),
                capture_output=True, text=True,
            )
            # Check ALL agents regardless of role
            checked: set[type] = set()
            for agent_label, agent_instance in [("executor", executor), ("reviewer", reviewer)]:
                agent_type = type(agent_instance)
                if agent_type in checked:
                    continue
                checked.add(agent_type)
                if isinstance(agent_instance, ClaudeCodeExecutor):
                    console.print(f"  Checking Claude Code ({agent_label})...")
                    ClaudeCodeExecutor.preflight_check(preflight_dir)
                    console.print("  [green]✓[/green] Claude Code: auth + files + commands")
                elif isinstance(agent_instance, CodexExecutor):
                    console.print(f"  Checking Codex ({agent_label})...")
                    CodexExecutor.preflight_check(preflight_dir)
                    console.print("  [green]✓[/green] Codex: auth + files + commands")
            import shutil as _shutil

            _shutil.rmtree(preflight_dir, ignore_errors=True)
        gates = GateRunner(gates=[BuildGate(), TestGate(), LintGate()])

        dispatcher = Dispatcher(
            executor=executor,
            reviewer=reviewer,
            gates=gates,
            workspace=workspace,
            config=config,
            git=git,
            queue_manager=qm,
            lock=lock,
        )

        now_str = datetime.now(tz=UTC).strftime("%Y-%m-%d")
        run_num = "001"
        worktree_base = root / "worktrees"
        run_dir_base = root / CONFIG_DIR / "runs" / now_str / run_num

        console.print(f"\n[bold green]Starting night run[/bold green] {'(mock)' if mock else ''}")
        results = dispatcher.run(worktree_base, run_dir_base)

        done = sum(1 for r in results if r.status.value == "done")
        failed = sum(1 for r in results if r.status.value == "failed")
        blocked = sum(1 for r in results if r.status.value == "blocked")

        console.print(f"\n[bold]Night run complete:[/bold] {done} done, {failed} failed, {blocked} blocked")
        exit_code = 0 if failed == 0 and blocked == 0 else 1
        raise typer.Exit(code=exit_code)

    except ValueError as e:
        console.print(f"\n[red]✗[/red] {e}")
        raise typer.Exit(code=1) from e
    except HpncError as e:
        console.print(f"\n[red]✗[/red] {e}")
        raise typer.Exit(code=e.exit_code) from e
