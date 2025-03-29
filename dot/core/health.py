"""Health check utilities for the Dot CLI tool."""

import os
import shutil
import subprocess
from typing import Dict, List, Tuple, Optional

from dot.cli.output import output_manager
from dot.utils.logger import logger


def check_git_installed() -> bool:
    """Check if git is installed."""
    return shutil.which("git") is not None


def check_dotfiles_dir() -> Tuple[bool, str]:
    """Check if ~/.dotfiles directory exists and is valid."""
    dotfiles_path = os.path.expanduser("~/.dotfiles")

    if not os.path.exists(dotfiles_path):
        return False, "missing"

    if not os.path.isdir(dotfiles_path):
        return False, "not_directory"

    # Check if it's a git repository
    git_dir = os.path.join(dotfiles_path, ".git")
    if not os.path.isdir(git_dir):
        return False, "not_git_repo"

    # Check if it has our specific structure
    required_dirs = ["user", "system"]
    required_files = ["README.md", "config.json"]

    missing_dirs = [
        d for d in required_dirs if not os.path.isdir(os.path.join(dotfiles_path, d))
    ]
    missing_files = [
        f for f in required_files if not os.path.isfile(os.path.join(dotfiles_path, f))
    ]

    if missing_dirs or missing_files:
        return False, "invalid_structure"

    return True, "valid"


def check_remote_configured() -> bool:
    """Check if a remote repository is configured."""
    try:
        dotfiles_path = os.path.expanduser("~/.dotfiles")
        result = subprocess.run(
            ["git", "remote", "-v"],
            cwd=dotfiles_path,
            capture_output=True,
            text=True,
            check=True,
        )
        return "origin" in result.stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def health_check(check_remote: bool = False) -> Dict[str, bool]:
    """Run all health checks and return results."""
    results = {
        "git_installed": check_git_installed(),
        "dotfiles_dir_valid": False,
    }

    if results["git_installed"]:
        valid, status = check_dotfiles_dir()
        results["dotfiles_dir_valid"] = valid
        results["dotfiles_dir_status"] = status

        if valid and check_remote:
            results["remote_configured"] = check_remote_configured()

    return results


def check_and_guide(check_remote: bool = False) -> bool:
    """Run health checks and provide guidance if needed."""
    results = health_check(check_remote)

    if not results["git_installed"]:
        output_manager.print_error("health_git_not_installed")
        return False

    if not results.get("dotfiles_dir_valid", False):
        status = results.get("dotfiles_dir_status", "unknown")
        output_manager.print_error(f"health_dotfiles_dir_{status}")
        output_manager.print("health_run_init")
        return False

    if check_remote and not results.get("remote_configured", False):
        output_manager.print_error("health_remote_not_configured")
        output_manager.print("health_run_remote")
        return False

    return True
