"""Global constants for HPNC."""

__all__ = [
    "APP_NAME",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "GATE_TIMEOUT",
    "GIT_TIMEOUT",
    "CLI_CHECK_TIMEOUT",
]

APP_NAME = "hpnc"
CONFIG_DIR = "_hpnc"
CONFIG_FILE = "config.yaml"

# Subprocess timeouts (seconds)
GATE_TIMEOUT = 300
"""Timeout for quality gate subprocess execution (build, test, lint)."""

GIT_TIMEOUT = 60
"""Timeout for git operations (branch, worktree, etc.)."""

CLI_CHECK_TIMEOUT = 10
"""Timeout for CLI version/connectivity checks."""
