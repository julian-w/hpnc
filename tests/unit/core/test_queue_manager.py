"""Tests for QueueManager — queue operations and frontmatter parsing."""

from pathlib import Path

import pytest

from hpnc.core.queue_manager import QueueManager, parse_frontmatter
from hpnc.infra.errors import ConfigError
from hpnc.infra.workspace import Workspace

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "stories"


def test_parse_frontmatter_valid_story() -> None:
    fm = parse_frontmatter(FIXTURES / "valid_night_ready.md")
    assert fm.night_ready is True
    assert fm.executor == "opus"
    assert fm.reviewer == "codex"
    assert fm.risk == "low"
    assert "build" in fm.gates_required


def test_parse_frontmatter_missing_fields_uses_defaults() -> None:
    fm = parse_frontmatter(FIXTURES / "missing_frontmatter.md")
    assert fm.night_ready is False
    assert fm.executor == ""
    assert fm.risk == "low"


def test_parse_frontmatter_no_frontmatter_returns_defaults() -> None:
    fm = parse_frontmatter(FIXTURES / "missing_frontmatter.md")
    assert fm.night_ready is False
    assert fm.tests_required is True


def _make_queue_manager(tmp_path: Path) -> tuple[QueueManager, Path]:
    """Create a QueueManager with a temp workspace."""
    ws = Workspace(root=tmp_path)
    queue_path = tmp_path / "_hpnc" / "night-queue.yaml"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text("tasks: []\n")
    return QueueManager(workspace=ws, queue_path=queue_path), queue_path


def _make_story(tmp_path: Path, name: str = "story.md") -> Path:
    """Create a minimal story file."""
    story = tmp_path / name
    story.write_text("---\nnight_ready: true\nexecutor: opus\n---\n\n# Test\n")
    return story


def test_add_story_to_empty_queue(tmp_path: Path) -> None:
    mgr, _ = _make_queue_manager(tmp_path)
    story = _make_story(tmp_path)
    assert mgr.add(story) is True
    tasks = mgr.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["night_ready"] is True


def test_add_story_appends_to_existing_queue(tmp_path: Path) -> None:
    mgr, _ = _make_queue_manager(tmp_path)
    s1 = _make_story(tmp_path, "story1.md")
    s2 = _make_story(tmp_path, "story2.md")
    mgr.add(s1)
    mgr.add(s2)
    tasks = mgr.list_tasks()
    assert len(tasks) == 2


def test_add_duplicate_story_returns_false(tmp_path: Path) -> None:
    mgr, _ = _make_queue_manager(tmp_path)
    story = _make_story(tmp_path)
    assert mgr.add(story) is True
    assert mgr.add(story) is False
    assert len(mgr.list_tasks()) == 1


def test_add_nonexistent_file_raises(tmp_path: Path) -> None:
    mgr, _ = _make_queue_manager(tmp_path)
    with pytest.raises(ConfigError, match="not found"):
        mgr.add(tmp_path / "nonexistent.md")


def test_add_non_markdown_raises(tmp_path: Path) -> None:
    mgr, _ = _make_queue_manager(tmp_path)
    txt_file = tmp_path / "readme.txt"
    txt_file.write_text("not a story")
    with pytest.raises(ConfigError, match="Not a markdown"):
        mgr.add(txt_file)
