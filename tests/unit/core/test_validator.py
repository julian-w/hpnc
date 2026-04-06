"""Tests for Validation Engine — pre-flight checks."""

from pathlib import Path

from hpnc.core.validator import Validator

FIXTURES = Path(__file__).parent.parent.parent / "fixtures" / "stories"


def _make_story(tmp_path: Path, frontmatter: str, name: str = "story.md") -> Path:
    """Create a story file with given frontmatter."""
    story = tmp_path / name
    story.write_text(f"---\n{frontmatter}\n---\n\n# Test Story\n")
    return story


def _make_task(story_path: Path) -> dict[str, object]:
    """Create a task dict for the queue."""
    return {"story": str(story_path)}


def test_validate_empty_queue(tmp_path: Path) -> None:
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([])
    assert not result.passed
    assert any("empty" in i.what.lower() for i in result.issues)


def test_validate_valid_story_passes(tmp_path: Path) -> None:
    story = _make_story(
        tmp_path,
        "night_ready: true\nexecutor: opus\nreviewer: codex\n"
        "tests_required: true\ngates_required: [build, tests, lint]",
    )
    # Create .pre-commit-config.yaml with secrets hook
    (tmp_path / ".pre-commit-config.yaml").write_text("hooks:\n  - id: gitleaks\n")
    # Init git for worktree check
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=str(tmp_path), capture_output=True, check=True)
    (tmp_path / "README.md").write_text("# T\n")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(tmp_path), capture_output=True, check=True)

    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    # Filter out agent connectivity issues — agents not installed in CI
    non_agent_issues = [i for i in result.issues if "not found" not in i.what]
    assert len(non_agent_issues) == 0, [f"{i.what}: {i.why}" for i in non_agent_issues]


def test_validate_missing_night_ready(tmp_path: Path) -> None:
    story = _make_story(tmp_path, "executor: opus\nreviewer: codex\ntests_required: true\ngates_required: [build]")
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    assert not result.passed
    assert any("night-ready" in i.what.lower() or "night_ready" in i.what.lower() for i in result.issues)


def test_validate_missing_mandatory_fields(tmp_path: Path) -> None:
    story = _make_story(tmp_path, "night_ready: true")
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    assert not result.passed
    mandatory_issues = [i for i in result.issues if "mandatory" in i.what.lower() or "Missing" in i.what]
    assert len(mandatory_issues) >= 1


def test_validate_blocking_questions_not_empty(tmp_path: Path) -> None:
    story = _make_story(
        tmp_path,
        "night_ready: true\nexecutor: opus\nreviewer: codex\n"
        "tests_required: true\ngates_required: [build]\n"
        "blocking_questions:\n  - How should auth work?",
    )
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    assert not result.passed
    assert any("blocking" in i.what.lower() for i in result.issues)


def test_validate_unknown_gate_warns(tmp_path: Path) -> None:
    story = _make_story(
        tmp_path,
        "night_ready: true\nexecutor: opus\nreviewer: codex\n"
        "tests_required: true\ngates_required: [build, storybook]",
    )
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    assert any("unknown gate" in i.what.lower() for i in result.issues)


def test_validate_story_not_found(tmp_path: Path) -> None:
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([{"story": str(tmp_path / "missing.md")}])
    assert not result.passed
    assert any("not found" in i.what.lower() for i in result.issues)


def test_validate_no_secrets_hook(tmp_path: Path) -> None:
    story = _make_story(
        tmp_path,
        "night_ready: true\nexecutor: opus\nreviewer: codex\n"
        "tests_required: true\ngates_required: [build]",
    )
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    assert any("secrets" in i.what.lower() or "pre-commit" in i.what.lower() for i in result.issues)


def test_validate_reports_all_failures(tmp_path: Path) -> None:
    """Validator must report ALL failures, not just the first."""
    story = _make_story(tmp_path, "executor: opus")  # Missing night_ready, reviewer, tests_required, gates
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    # Should have multiple issues
    assert len(result.issues) >= 3


def test_validate_issues_have_what_why_action(tmp_path: Path) -> None:
    story = _make_story(tmp_path, "night_ready: false")
    validator = Validator(project_root=tmp_path)
    result = validator.validate_queue([_make_task(story)])
    for issue in result.issues:
        assert issue.what, "Issue must have 'what'"
        assert issue.why, "Issue must have 'why'"
        assert issue.action, "Issue must have 'action'"
