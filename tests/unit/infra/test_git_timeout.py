"""Tests for git timeout handling."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from hpnc.infra.errors import HpncError
from hpnc.infra.git import GitWrapper


@patch("hpnc.infra.git.subprocess.run")
def test_git_timeout_raises_hpnc_error(mock_run: object) -> None:
    # On Windows, constructor calls _enable_longpaths (1 extra subprocess call)
    side_effects: list[object] = []
    if sys.platform == "win32":
        side_effects.append(subprocess.CompletedProcess(args=[], returncode=0))
    side_effects.append(subprocess.TimeoutExpired(cmd="git branch", timeout=60))

    mock_run.side_effect = side_effects  # type: ignore[union-attr]
    gw = GitWrapper(repo_root=Path("/fake"))
    with pytest.raises(HpncError, match="timed out"):
        gw.create_branch("test")
