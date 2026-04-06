"""Tests for Workspace error paths."""

from pathlib import Path

import pytest

from hpnc.infra.errors import ConfigError
from hpnc.infra.workspace import Workspace


def test_workspace_read_yaml_non_dict_raises(tmp_path: Path) -> None:
    """YAML file containing a list should raise ConfigError."""
    (tmp_path / "list.yaml").write_text("- item1\n- item2\n")
    ws = Workspace(root=tmp_path)
    with pytest.raises(ConfigError, match="Unexpected YAML"):
        ws.read_yaml(Path("list.yaml"))


def test_workspace_read_yaml_empty_file_returns_empty(tmp_path: Path) -> None:
    """Empty YAML file should return empty dict."""
    (tmp_path / "empty.yaml").write_text("")
    ws = Workspace(root=tmp_path)
    result = ws.read_yaml(Path("empty.yaml"))
    assert result == {}


def test_workspace_read_yaml_invalid_yaml_raises(tmp_path: Path) -> None:
    (tmp_path / "bad.yaml").write_text(":\n  bad: [yaml\n  broken")
    ws = Workspace(root=tmp_path)
    with pytest.raises(ConfigError, match="parse"):
        ws.read_yaml(Path("bad.yaml"))


def test_workspace_write_yaml_atomic_creates_parent_dirs(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path)
    ws.write_yaml_atomic(Path("deep/nested/file.yaml"), {"key": "value"})
    assert (tmp_path / "deep" / "nested" / "file.yaml").exists()


def test_workspace_absolute_path_bypasses_root(tmp_path: Path) -> None:
    ws = Workspace(root=tmp_path / "root")
    target = tmp_path / "outside" / "file.yaml"
    target.parent.mkdir(parents=True)
    target.write_text("key: value\n")
    result = ws.read_yaml(target)
    assert result == {"key": "value"}
