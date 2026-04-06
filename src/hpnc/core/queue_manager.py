"""Queue Manager — manages the night queue of story tasks (FR9-FR17).

Handles frontmatter parsing, queue add/list, and duplicate detection.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from hpnc.infra.errors import ConfigError
from hpnc.infra.workspace import Workspace
from hpnc.schemas.frontmatter import FrontmatterSchema

__all__ = ["QueueManager"]


def parse_frontmatter(story: Path) -> FrontmatterSchema:
    """Extract YAML frontmatter from a story markdown file.

    Reads the block between the first two `---` delimiters.
    Missing fields use FrontmatterSchema defaults.

    Args:
        story: Path to the story markdown file.

    Returns:
        Parsed frontmatter as a FrontmatterSchema instance.
    """
    content = story.read_text(encoding="utf-8")
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        return FrontmatterSchema()

    end_idx = -1
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx < 0:
        return FrontmatterSchema()

    frontmatter_text = "\n".join(lines[1:end_idx])
    try:
        raw = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return FrontmatterSchema()

    if not isinstance(raw, dict):
        return FrontmatterSchema()

    return FrontmatterSchema(
        night_ready=raw.get("night_ready", False),
        executor=raw.get("executor", ""),
        reviewer=raw.get("reviewer", ""),
        risk=raw.get("risk", "low"),
        tests_required=raw.get("tests_required", True),
        touches=raw.get("touches", []),
        blocking_questions=raw.get("blocking_questions", []),
        gates_required=raw.get("gates_required", []),
    )


class QueueManager:
    """Manages the night queue of story tasks.

    Args:
        workspace: Workspace for atomic file operations.
        queue_path: Path to the night-queue.yaml file.
    """

    def __init__(self, workspace: Workspace, queue_path: Path) -> None:
        self.workspace = workspace
        self.queue_path = queue_path

    def _read_queue(self) -> list[dict[str, Any]]:
        """Read current queue tasks.

        Returns:
            List of task dicts from the queue file.
        """
        try:
            data = self.workspace.read_yaml(self.queue_path)
        except ConfigError:
            return []
        tasks = data.get("tasks", [])
        return tasks if isinstance(tasks, list) else []

    def add(self, story: Path) -> bool:
        """Add a story to the night queue.

        Validates the story file exists and is markdown, parses frontmatter,
        checks for duplicates, and appends to the queue.

        Args:
            story: Path to the story markdown file.

        Returns:
            True if the story was added, False if it was a duplicate.

        Raises:
            ConfigError: If the story file doesn't exist or isn't markdown.
        """
        resolved = story.resolve()

        if not resolved.exists():
            raise ConfigError(
                what=f"Story file not found: {resolved}",
                why="The file does not exist",
                action="Check the file path and try again",
            )

        if resolved.suffix.lower() != ".md":
            raise ConfigError(
                what=f"Not a markdown file: {resolved}",
                why=f"Expected .md extension, got '{resolved.suffix}'",
                action="Provide a markdown (.md) story file",
            )

        tasks = self._read_queue()

        story_str = str(resolved)
        for task in tasks:
            if task.get("story") == story_str:
                return False

        frontmatter = parse_frontmatter(resolved)

        entry: dict[str, Any] = {
            "story": story_str,
            "night_ready": frontmatter.night_ready,
            "executor": frontmatter.executor,
            "reviewer": frontmatter.reviewer,
            "risk": frontmatter.risk,
            "tests_required": frontmatter.tests_required,
        }

        tasks.append(entry)
        self.workspace.write_yaml_atomic(self.queue_path, {"tasks": tasks})
        return True

    def list_tasks(self) -> list[dict[str, Any]]:
        """List all tasks currently in the queue.

        Returns:
            List of task dicts.
        """
        return self._read_queue()
