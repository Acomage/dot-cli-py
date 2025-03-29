"""File synchronization utilities for the Dot CLI tool."""

import os
import shutil
from typing import Tuple, List, Optional

from dot.cli.output import output_manager
from dot.core.config import config_manager
from dot.core.conflict import conflict_manager
from dot.utils.logger import logger


class SyncManager:
    """Manage file synchronization between system and repository."""

    def __init__(self) -> None:
        """Initialize the sync manager."""
        self.dotfiles_path = os.path.expanduser("~/.dotfiles")
        self.user_repo_path = os.path.join(self.dotfiles_path, "user")
        self.system_repo_path = os.path.join(self.dotfiles_path, "system")

    def _get_repo_path(self, original_path: str) -> str:
        """Get the path to the repository version of a file."""
        real_path = os.path.expanduser(original_path)

        # Determine if this is a user or system file
        if real_path.startswith(os.path.expanduser("~")):
            # User file
            rel_path = os.path.relpath(real_path, os.path.expanduser("~"))
            return os.path.join(self.user_repo_path, rel_path)
        else:
            # System file
            rel_path = real_path.lstrip("/")
            return os.path.join(self.system_repo_path, rel_path)

    def _ensure_parent_dirs(self, path: str) -> None:
        """Ensure parent directories of a path exist."""
        parent_dir = os.path.dirname(path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

    def copy_to_repo(self, path: str) -> bool:
        """Copy a file from the system to the repository."""
        real_path = os.path.expanduser(path)
        repo_path = self._get_repo_path(real_path)

        # Check if file exists
        if not os.path.exists(real_path):
            logger.error(f"File not found: {path}")
            return False

        try:
            # Create parent directories if needed
            self._ensure_parent_dirs(repo_path)

            # Check if it's a conflict file
            if config_manager.is_conflict(real_path):
                conflict_path = conflict_manager._get_conflict_file_path(real_path)

                # Ensure conflict directory exists
                self._ensure_parent_dirs(conflict_path)

                # Copy to conflict directory
                if os.path.isdir(real_path):
                    if os.path.exists(conflict_path):
                        shutil.rmtree(conflict_path)
                    shutil.copytree(real_path, conflict_path)
                else:
                    shutil.copy2(real_path, conflict_path)

                # Merge conflict file with repo file
                conflict_manager.merge_conflict_files(real_path)
            else:
                # Regular file - copy directly to repo
                if os.path.isdir(real_path):
                    if os.path.exists(repo_path):
                        shutil.rmtree(repo_path)
                    shutil.copytree(real_path, repo_path)
                else:
                    shutil.copy2(real_path, repo_path)

            return True
        except Exception as e:
            logger.error(f"Error copying to repository: {e}")
            return False

    def copy_from_repo(self, path: str, confirm: bool = True) -> bool:
        """
        Copy a file from the repository to the system.

        Args:
            path: Path to the file
            confirm: Whether to prompt for confirmation if the destination doesn't exist

        Returns:
            bool: Success state
        """
        real_path = os.path.expanduser(path)
        repo_path = self._get_repo_path(real_path)

        # Check if repo file exists
        if not os.path.exists(repo_path):
            logger.error(f"Repository file not found for: {path}")
            return False

        # Check if destination exists and prompt if necessary
        if not os.path.exists(real_path):
            parent_dir = os.path.dirname(real_path)
            if not os.path.exists(parent_dir):
                if confirm:
                    response = output_manager.prompt(
                        "sync_create_directory", path=parent_dir, choices="y/n/a"
                    ).lower()

                    if response == "n":
                        return False
                    elif response == "a":
                        # Set confirm to False for future calls
                        confirm = False

                # Create parent directory
                os.makedirs(parent_dir, exist_ok=True)

        try:
            # Check if it's a conflict file
            if config_manager.is_conflict(real_path):
                conflict_path = conflict_manager._get_conflict_file_path(real_path)

                # Check if conflict file exists, otherwise initialize it
                if not os.path.exists(conflict_path):
                    conflict_manager.initialize_conflict(real_path)

                # Copy from conflict directory to system
                if os.path.isdir(conflict_path):
                    if os.path.exists(real_path):
                        shutil.rmtree(real_path)
                    shutil.copytree(conflict_path, real_path)
                else:
                    shutil.copy2(conflict_path, real_path)
            else:
                # Regular file - copy directly from repo
                if os.path.isdir(repo_path):
                    if os.path.exists(real_path):
                        shutil.rmtree(real_path)
                    shutil.copytree(repo_path, real_path)
                else:
                    shutil.copy2(repo_path, real_path)

            return True
        except Exception as e:
            logger.error(f"Error copying from repository: {e}")
            return False

    def diff_files(self, path: str) -> Tuple[bool, Optional[str]]:
        """Compare a file in the system with its repository version."""
        real_path = os.path.expanduser(path)
        repo_path = self._get_repo_path(real_path)

        # Check if both files exist
        if not os.path.exists(real_path):
            return False, f"System file not found: {path}"

        if not os.path.exists(repo_path):
            return False, f"Repository file not found for: {path}"

        # For directories, we can't easily show a diff
        if os.path.isdir(real_path):
            return False, f"Cannot diff directory: {path}"

        try:
            import difflib

            # Read system file
            with open(real_path, "r", encoding="utf-8") as f:
                system_lines = f.readlines()

            # Read repository file
            with open(repo_path, "r", encoding="utf-8") as f:
                repo_lines = f.readlines()

            # Generate diff
            diff = difflib.unified_diff(
                repo_lines,
                system_lines,
                fromfile=f"repo:{path}",
                tofile=f"system:{path}",
                lineterm="",
            )

            return True, "\n".join(diff)
        except Exception as e:
            logger.error(f"Error comparing files: {e}")
            return False, f"Error: {str(e)}"


# Create a global instance for use throughout the application
sync_manager = SyncManager()
