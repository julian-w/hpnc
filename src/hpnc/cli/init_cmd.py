"""hpnc init — project setup command (FR1, FR5, NFR16).

Creates _hpnc/ directory with config, executor instructions, and queue.
Runs connectivity checks for AI agent CLIs. Safe to re-run.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from rich.console import Console

from hpnc.infra.config import CONFIG_DIR, CONFIG_FILE

__all__ = ["run_init"]

_EXECUTOR_INSTRUCTIONS_TEMPLATE = """\
# Executor Instructions

These instructions are provided to AI agents during night runs.

## Rules

- Follow the project's coding conventions
- Run tests before committing
- Do not modify files outside the task's worktree
- Use conventional commit messages
- Write Google-style docstrings on all public functions
"""

_EMPTY_QUEUE = "tasks: []\n"


def _detect_project_name(project_root: Path) -> str:
    """Detect project name from directory name.

    Args:
        project_root: Path to the project root.

    Returns:
        Detected project name.
    """
    return project_root.name


def _check_cli(name: str, command: list[str], console: Console) -> bool:
    """Check if a CLI tool is installed and reachable.

    Args:
        name: Display name of the tool.
        command: Command to run for version check.
        console: Rich console for output.

    Returns:
        True if the tool is reachable.
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            console.print(f"  [green]✓[/green] {name}: {version}")
            return True
        console.print(f"  [yellow]![/yellow] {name}: returned exit code {result.returncode}")
        return False
    except FileNotFoundError:
        console.print(f"  [yellow]![/yellow] {name}: not found (can be installed later)")
        return False


def _detect_bmad(project_root: Path, console: Console) -> None:
    """Detect and report existing BMAD configuration.

    Args:
        project_root: Path to the project root.
        console: Rich console for output.
    """
    bmad_dir = project_root / "_bmad"
    claude_skills = project_root / ".claude" / "skills"

    if bmad_dir.exists():
        console.print("  [green]✓[/green] BMAD configuration detected (_bmad/)")
    elif claude_skills.exists() and any(claude_skills.glob("bmad-*")):
        console.print("  [green]✓[/green] BMAD skills detected (.claude/skills/bmad-*)")
    else:
        console.print("  [dim]—[/dim] No BMAD configuration found")


def run_init(project_root: Path | None = None, console: Console | None = None) -> None:
    """Initialize HPNC in the project.

    Creates _hpnc/ directory with configuration files if they don't exist.
    Runs connectivity checks regardless of initialization state.
    Safe to re-run — never overwrites existing files (NFR16).

    Args:
        project_root: Project root directory. Defaults to cwd.
        console: Rich console for output. Creates one if not provided.
    """
    root = (project_root or Path.cwd()).resolve()
    con = console or Console()

    hpnc_dir = root / CONFIG_DIR
    config_path = hpnc_dir / CONFIG_FILE
    instructions_path = hpnc_dir / "executor-instructions.md"
    queue_path = hpnc_dir / "night-queue.yaml"

    already_initialized = config_path.exists()

    if already_initialized:
        con.print(f"\n[bold]HPNC already initialized[/bold] in {root}")
        con.print("  Existing configuration preserved.")
    else:
        hpnc_dir.mkdir(parents=True, exist_ok=True)
        project_name = _detect_project_name(root)

        config_path.write_text(
            f"project_name: {project_name}\n", encoding="utf-8"
        )
        con.print(f"\n[bold green]HPNC initialized[/bold green] in {root}")
        con.print(f"  Created {CONFIG_DIR}/{CONFIG_FILE}")

    if not instructions_path.exists():
        instructions_path.write_text(
            _EXECUTOR_INSTRUCTIONS_TEMPLATE, encoding="utf-8"
        )
        con.print(f"  Created {CONFIG_DIR}/executor-instructions.md")

    if not queue_path.exists():
        queue_path.write_text(_EMPTY_QUEUE, encoding="utf-8")
        con.print(f"  Created {CONFIG_DIR}/night-queue.yaml")

    # Connectivity checks (always run)
    con.print("\n[bold]Agent connectivity:[/bold]")
    _check_cli("Claude Code", ["claude", "--version"], con)
    _check_cli("Codex", ["codex", "--version"], con)

    # BMAD detection
    con.print("\n[bold]Integration:[/bold]")
    _detect_bmad(root, con)

    # Next steps
    if not already_initialized:
        con.print("\n[bold]Next steps:[/bold]")
        con.print("  1. Edit _hpnc/config.yaml to customize settings")
        con.print("  2. Edit _hpnc/executor-instructions.md with project rules")
        con.print("  3. Add stories: hpnc queue add <story.md>")
        con.print("  4. Validate: hpnc validate")
        con.print("  5. Run: hpnc start --mock")
