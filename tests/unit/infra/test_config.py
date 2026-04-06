"""Tests for ConfigLoader — project root discovery and config loading."""

from pathlib import Path

import pytest

from hpnc.infra.config import ConfigLoader
from hpnc.infra.errors import ConfigError


def _create_config(root: Path, content: str = "project_name: test\n") -> None:
    """Create _hpnc/config.yaml in the given root."""
    config_dir = root / "_hpnc"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "config.yaml").write_text(content)


def test_find_root_from_project_root(tmp_path: Path) -> None:
    _create_config(tmp_path)
    loader = ConfigLoader()
    root = loader.find_root(start=tmp_path)
    assert root == tmp_path.resolve()


def test_find_root_from_nested_subdir(tmp_path: Path) -> None:
    _create_config(tmp_path)
    nested = tmp_path / "src" / "hpnc" / "core"
    nested.mkdir(parents=True)
    loader = ConfigLoader()
    root = loader.find_root(start=nested)
    assert root == tmp_path.resolve()


def test_find_root_missing_raises_config_error(tmp_path: Path) -> None:
    loader = ConfigLoader()
    with pytest.raises(ConfigError, match="HPNC project not found"):
        loader.find_root(start=tmp_path)


def test_load_merges_defaults(tmp_path: Path) -> None:
    _create_config(tmp_path, "project_name: myproject\n")
    loader = ConfigLoader()
    config = loader.load(tmp_path)
    assert config.project_name == "myproject"
    assert config.merge_target == "main"
    assert config.log_verbosity == "normal"
    assert config.timeout == "30m"
    assert config.max_fix_attempts == 3
    assert config.executor == "opus"
    assert config.reviewer == "codex"


def test_load_file_overrides_defaults(tmp_path: Path) -> None:
    _create_config(
        tmp_path,
        "project_name: custom\nmerge_target: develop\ntimeout: 60m\n",
    )
    loader = ConfigLoader()
    config = loader.load(tmp_path)
    assert config.project_name == "custom"
    assert config.merge_target == "develop"
    assert config.timeout == "60m"


def test_load_missing_project_name_raises(tmp_path: Path) -> None:
    _create_config(tmp_path, "merge_target: main\n")
    loader = ConfigLoader()
    with pytest.raises(ConfigError, match="project_name"):
        loader.load(tmp_path)


def test_load_malformed_yaml_raises(tmp_path: Path) -> None:
    _create_config(tmp_path, ":\n  bad: [yaml\n  broken")
    loader = ConfigLoader()
    with pytest.raises(ConfigError, match="parse"):
        loader.load(tmp_path)


def test_load_resolves_project_root_as_path(tmp_path: Path) -> None:
    _create_config(tmp_path)
    loader = ConfigLoader()
    config = loader.load(tmp_path)
    assert isinstance(config.project_root, Path)
    assert config.project_root.is_absolute()
