"""Tests for git timeout handling."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from hpnc.infra.errors import HpncError
from hpnc.infra.git import GitWrapper


@patch("hpnc.infra.git.subprocess.run")
def test_git_timeout_raises_hpnc_error(mock_run: object) -> None:
    # First call is _enable_longpaths on Windows (allow it)
    # Second call is the actual git command (timeout)
    mock_run.side_effect = [  # type: ignore[union-attr]
        subprocess.CompletedProcess(args=[], returncode=0),
        subprocess.TimeoutExpired(cmd="git branch", timeout=60),
    ]
    gw = GitWrapper(repo_root=Path("/fake"))
    with pytest.raises(HpncError, match="timed out"):
        gw.create_branch("test")
