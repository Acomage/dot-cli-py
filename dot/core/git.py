"""Git operations for the Dot CLI tool."""

import os
import subprocess
from typing import List, Optional, Tuple

from dot.cli.output import output_manager
from dot.utils.logger import logger


class GitManager:
    """Manage Git operations for the dotfiles repository."""

    def __init__(self) -> None:
        """Initialize the Git manager."""
        self.dotfiles_path = os.path.expanduser("~/.dotfiles")

    def _run_git_command(self, args: List[str], check: bool = True) -> Tuple[bool, str]:
        """Run a git command and return the result."""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.dotfiles_path,
                capture_output=True,
                text=True,
                check=check,
            )
            return True, result.stdout.strip()
        except subprocess.SubprocessError as e:
            error_msg = str(e)
            if hasattr(e, "stderr"):
                error_msg = e.stderr.strip()
            return False, error_msg

    def init(self) -> Tuple[bool, str]:
        """Initialize a new Git repository."""
        if not os.path.exists(self.dotfiles_path):
            os.makedirs(self.dotfiles_path, exist_ok=True)

        # Initialize repository
        success, output = self._run_git_command(["init", "-b", "main"])
        if not success:
            return False, output

        # Configure user information if not set
        self._configure_user_if_needed()

        return True, output

    def _configure_user_if_needed(self) -> None:
        """Configure Git user information if not already set."""
        # Check if user.name is set
        success, name = self._run_git_command(["config", "user.name"], check=False)
        if not success or not name:
            # Prompt for user name
            user_name = output_manager.prompt("git_prompt_name")
            if user_name:
                self._run_git_command(["config", "user.name", user_name])

        # Check if user.email is set
        success, email = self._run_git_command(["config", "user.email"], check=False)
        if not success or not email:
            # Prompt for user email
            user_email = output_manager.prompt("git_prompt_email")
            if user_email:
                self._run_git_command(["config", "user.email", user_email])

    def add(self, path: str = ".") -> Tuple[bool, str]:
        """Add files to the Git index."""
        return self._run_git_command(["add", path])

    def commit(self, message: str) -> Tuple[bool, str]:
        """Commit changes to the repository."""
        return self._run_git_command(["commit", "-m", message])

    def add_and_commit(self, message: str, path: str = ".") -> Tuple[bool, str]:
        """Add files and commit changes to the repository."""
        # Add files
        success, output = self.add(path)
        if not success:
            return False, output

        # Check if there are changes to commit
        success, status_output = self._run_git_command(["status", "--porcelain"])
        if not success:
            return False, status_output

        if not status_output:
            # No changes to commit
            return True, "No changes to commit"

        # Commit changes
        return self.commit(message)

    def set_remote(self, url: str) -> Tuple[bool, str]:
        """Set the remote repository URL."""
        # Check if remote exists
        success, remote_output = self._run_git_command(["remote"], check=False)

        if "origin" in remote_output:
            # Update existing remote
            return self._run_git_command(["remote", "set-url", "origin", url])
        else:
            # Add new remote
            return self._run_git_command(["remote", "add", "origin", url])

    def remove_remote(self) -> Tuple[bool, str]:
        """Remove the remote repository."""
        # Check if remote exists
        success, remote_output = self._run_git_command(["remote"], check=False)

        if "origin" in remote_output:
            return self._run_git_command(["remote", "remove", "origin"])

        return True, "No remote to remove"

    def push(self) -> Tuple[bool, str]:
        """Push changes to the remote repository."""
        # Check if remote exists
        success, remote_output = self._run_git_command(["remote"], check=False)

        if "origin" not in remote_output:
            return False, "No remote repository configured"

        # Push changes
        return self._run_git_command(["push", "-u", "origin", "main"])

    def pull(self) -> Tuple[bool, str]:
        """Pull changes from the remote repository."""
        # Check if remote exists
        success, remote_output = self._run_git_command(["remote"], check=False)

        if "origin" not in remote_output:
            return False, "No remote repository configured"

        # Pull changes
        return self._run_git_command(["pull", "origin", "main"])

    def clone(self, url: str, path: Optional[str] = None) -> Tuple[bool, str]:
        """Clone a remote repository."""
        if path is None:
            path = self.dotfiles_path

        # Create parent directory if it doesn't exist
        parent_dir = os.path.dirname(path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        # Clone repository
        try:
            result = subprocess.run(
                ["git", "clone", url, path],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, result.stdout.strip()
        except subprocess.SubprocessError as e:
            error_msg = str(e)
            if hasattr(e, "stderr"):
                error_msg = e.stderr.strip()
            return False, error_msg

    def get_status(self) -> Tuple[bool, str]:
        """Get the status of the repository."""
        return self._run_git_command(["status", "--short"])


# Create a global instance for use throughout the application
git_manager = GitManager()
