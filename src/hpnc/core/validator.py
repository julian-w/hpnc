"""Validation Engine — pre-flight checks before night run (FR18-FR25).

Pure read-only operation (NFR15). Reports all failures, not just the first.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hpnc.core.queue_manager import parse_frontmatter
from hpnc.schemas.frontmatter import KNOWN_GATES, MANDATORY_FIELDS

__all__ = ["ValidationResult", "Validator"]


@dataclass
class ValidationIssue:
    """A single validation failure.

    Args:
        story: Path to the story file (or "environment" for system checks).
        what: What failed.
        why: Why it failed.
        action: What to do about it.
    """

    story: str
    what: str
    why: str
    action: str


@dataclass
class ValidationResult:
    """Aggregated validation results.

    Args:
        issues: List of validation issues found.
    """

    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """True only when zero issues found."""
        return len(self.issues) == 0

    def add(self, story: str, what: str, why: str, action: str) -> None:
        """Add a validation issue.

        Args:
            story: Story path or "environment".
            what: What failed.
            why: Why it failed.
            action: Suggested fix.
        """
        self.issues.append(ValidationIssue(
            story=story, what=what, why=why, action=action,
        ))


class Validator:
    """Pre-flight validation for night run readiness.

    All checks are read-only — no files are modified (NFR15).

    Args:
        project_root: Path to the project root.
    """

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def validate_queue(self, tasks: list[dict[str, Any]]) -> ValidationResult:
        """Validate all queued tasks and environment.

        Args:
            tasks: List of task dicts from night-queue.yaml.

        Returns:
            ValidationResult with all issues found.
        """
        result = ValidationResult()

        if not tasks:
            result.add(
                story="queue",
                what="Queue is empty",
                why="No tasks in night-queue.yaml",
                action="Add stories with 'hpnc queue add <story.md>'",
            )
            return result

        for task in tasks:
            story_path = task.get("story", "")
            self._validate_story(story_path, result)

        self._validate_worktree_availability(result)
        self._validate_secrets_hook(result)

        return result

    def _validate_story(self, story_path: str, result: ValidationResult) -> None:
        """Validate a single story's frontmatter.

        Args:
            story_path: Path to the story file.
            result: ValidationResult to append issues to.
        """
        path = Path(story_path)
        if not path.exists():
            result.add(
                story=story_path,
                what="Story file not found",
                why=f"File does not exist: {story_path}",
                action="Check the file path or remove from queue",
            )
            return

        fm = parse_frontmatter(path)

        # FR19: night_ready must be true
        if not fm.night_ready:
            result.add(
                story=story_path,
                what="Story not night-ready",
                why="night_ready is not set to true",
                action="Set 'night_ready: true' in story frontmatter",
            )

        # FR20: mandatory fields present
        fm_dict = {
            "night_ready": fm.night_ready,
            "executor": fm.executor,
            "reviewer": fm.reviewer,
            "tests_required": fm.tests_required,
            "gates_required": fm.gates_required,
        }
        for field_name in MANDATORY_FIELDS:
            value = fm_dict.get(field_name)
            if value is None or value == "" or value == []:
                result.add(
                    story=story_path,
                    what=f"Missing mandatory field: {field_name}",
                    why=f"Field '{field_name}' is empty or missing",
                    action=f"Add '{field_name}' to story frontmatter",
                )

        # FR21: blocking_questions must be empty
        if fm.blocking_questions:
            result.add(
                story=story_path,
                what="Blocking questions not resolved",
                why=f"{len(fm.blocking_questions)} blocking question(s) remain",
                action="Resolve all blocking questions before night run",
            )

        # FR22: tests_required must be defined
        # (already checked via mandatory fields above)

        # Validate gates_required against known gates
        for gate in fm.gates_required:
            if gate not in KNOWN_GATES:
                result.add(
                    story=story_path,
                    what=f"Unknown gate: {gate}",
                    why=f"Gate '{gate}' is not in known gates: {sorted(KNOWN_GATES)}",
                    action=f"Use one of: {', '.join(sorted(KNOWN_GATES))}",
                )

    def _validate_worktree_availability(self, result: ValidationResult) -> None:
        """Check that Git worktrees can be created (FR23).

        Args:
            result: ValidationResult to append issues to.
        """
        try:
            proc = subprocess.run(
                ["git", "worktree", "list"],
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )
            if proc.returncode != 0:
                result.add(
                    story="environment",
                    what="Git worktree not available",
                    why=proc.stderr.strip() or "git worktree command failed",
                    action="Ensure you are in a Git repository with worktree support",
                )
        except FileNotFoundError:
            result.add(
                story="environment",
                what="Git not found",
                why="git command not found on PATH",
                action="Install Git (version 2.20+)",
            )

    def _validate_secrets_hook(self, result: ValidationResult) -> None:
        """Check that a secrets pre-commit hook is active (FR24).

        Args:
            result: ValidationResult to append issues to.
        """
        config_path = self.project_root / ".pre-commit-config.yaml"
        if not config_path.exists():
            result.add(
                story="environment",
                what="No pre-commit config found",
                why=".pre-commit-config.yaml not found in project root",
                action="Create .pre-commit-config.yaml with a secrets hook (git-secrets or gitleaks)",
            )
            return

        content = config_path.read_text(encoding="utf-8")
        if "git-secrets" not in content and "gitleaks" not in content:
            result.add(
                story="environment",
                what="No secrets hook configured",
                why="No git-secrets or gitleaks hook found in .pre-commit-config.yaml",
                action="Add a secrets detection hook to .pre-commit-config.yaml",
            )
