"""Conflict management for the Dot CLI tool."""

import os
import re
import shutil
from typing import List, Tuple, Optional, Dict

from dot.cli.output import output_manager
from dot.utils.logger import logger

# Magic string for conflict markers
MAGIC_STRING = "YuriSaveTheWorld"

# Regular expressions for conflict markers
LINE_MARKER_REGEX = re.compile(f"//({MAGIC_STRING})(.*)$")
BLOCK_START_REGEX = re.compile(f"/\\*({MAGIC_STRING})$")
BLOCK_END_REGEX = re.compile(f"({MAGIC_STRING})\\*/$")


class ConflictManager:
    """Manage conflicts between different machines."""

    def __init__(self) -> None:
        """Initialize the conflict manager."""
        self.dotfiles_path = os.path.expanduser("~/.dotfiles")
        self.conflict_path = os.path.join(self.dotfiles_path, "conflict")
        self.user_conflict_path = os.path.join(self.conflict_path, "user")
        self.system_conflict_path = os.path.join(self.conflict_path, "system")

        # Ensure conflict directories exist
        # for path in [
        #     self.conflict_path,
        #     self.user_conflict_path,
        #     self.system_conflict_path,
        # ]:
        #     if not os.path.exists(path):
        #         os.makedirs(path, exist_ok=True)

    def _get_conflict_file_path(self, original_path: str) -> str:
        """Get the path to the conflict version of a file."""
        real_path = os.path.expanduser(original_path)

        # Determine if this is a user or system file
        if real_path.startswith(os.path.expanduser("~")):
            # User file
            rel_path = os.path.relpath(real_path, os.path.expanduser("~"))
            return os.path.join(self.user_conflict_path, rel_path)
        else:
            # System file
            rel_path = real_path.lstrip("/")
            return os.path.join(self.system_conflict_path, rel_path)

    def _get_repo_file_path(self, original_path: str) -> str:
        """Get the path to the repository version of a file."""
        real_path = os.path.expanduser(original_path)

        # Determine if this is a user or system file
        if real_path.startswith(os.path.expanduser("~")):
            # User file
            rel_path = os.path.relpath(real_path, os.path.expanduser("~"))
            return os.path.join(self.dotfiles_path, "user", rel_path)
        else:
            # System file
            rel_path = real_path.lstrip("/")
            return os.path.join(self.dotfiles_path, "system", rel_path)

    def initialize_conflict(self, path: str) -> bool:
        """Initialize conflict markers for a file."""
        real_path = os.path.expanduser(path)

        # Check if file exists
        if not os.path.exists(real_path) or not os.path.isfile(real_path):
            logger.error(f"File not found: {path}")
            return False

        # Get conflict and repo file paths
        conflict_file_path = self._get_conflict_file_path(real_path)
        repo_file_path = self._get_repo_file_path(real_path)

        # Create directories if needed
        os.makedirs(os.path.dirname(conflict_file_path), exist_ok=True)

        # Copy repo file to conflict file
        try:
            shutil.copy2(repo_file_path, conflict_file_path)
            return True
        except (OSError, shutil.Error) as e:
            logger.error(f"Error copying file: {e}")
            return False

    def validate_conflict_markers(self, content: str) -> bool:
        """Validate that conflict markers are properly formatted."""
        lines = content.splitlines()
        in_block = False

        for line in lines:
            # Check for line markers
            line_match = LINE_MARKER_REGEX.search(line)
            if line_match:
                # Line marker is valid
                continue

            # Check for block markers
            block_start_match = BLOCK_START_REGEX.search(line)
            if block_start_match:
                if in_block:
                    # Nested blocks are not allowed
                    return False
                in_block = True
                continue

            block_end_match = BLOCK_END_REGEX.search(line)
            if block_end_match:
                if not in_block:
                    # End marker without start marker
                    return False
                in_block = False
                continue

        # Check if all blocks are closed
        return not in_block

    def merge_conflict_files(self, path: str) -> bool:
        """Merge conflict file with repository file."""
        conflict_file_path = self._get_conflict_file_path(path)
        repo_file_path = self._get_repo_file_path(path)

        # Check if both files exist
        if not os.path.exists(conflict_file_path) or not os.path.exists(repo_file_path):
            logger.error(f"Conflict or repository file not found for: {path}")
            return False

        try:
            # Read conflict file
            with open(conflict_file_path, "r", encoding="utf-8") as f:
                conflict_content = f.read()

            # Read repository file
            with open(repo_file_path, "r", encoding="utf-8") as f:
                repo_content = f.read()

            # Split files by conflict markers
            conflict_blocks = self._split_by_markers(conflict_content)
            repo_blocks = self._split_by_markers(repo_content)

            # Validate blocks have the same structure
            if len(conflict_blocks) != len(repo_blocks):
                logger.error(
                    "Conflict and repository files have different marker structures"
                )
                return False

            # Merge non-conflict parts
            merged_blocks = []
            for i in range(len(conflict_blocks)):
                if i % 2 == 0:  # Non-conflict block
                    merged_blocks.append(conflict_blocks[i])
                else:  # Conflict block
                    merged_blocks.append(repo_blocks[i])

            # Join blocks and write to repository file
            merged_content = "".join(merged_blocks)
            with open(repo_file_path, "w", encoding="utf-8") as f:
                f.write(merged_content)

            return True
        except Exception as e:
            logger.error(f"Error merging conflict files: {e}")
            return False

    def _split_by_markers(self, content: str) -> List[str]:
        """Split content by conflict markers."""
        # This splits content into alternating parts:
        # [non-conflict, conflict, non-conflict, conflict, ...]

        result = []
        lines = content.splitlines(True)  # Keep line endings

        buffer = ""
        in_block = False

        for line in lines:
            # Check for line markers
            line_match = LINE_MARKER_REGEX.search(line)
            if line_match and not in_block:
                # Found a single-line marker - split here
                if buffer:
                    result.append(buffer)
                    buffer = ""

                # Add this line as a conflict block
                result.append(line)
                continue

            # Check for block start marker
            block_start_match = BLOCK_START_REGEX.search(line)
            if block_start_match and not in_block:
                in_block = True

                # Add previous buffer to results
                if buffer:
                    result.append(buffer)

                # Start new buffer with this line
                buffer = line
                continue

            # Check for block end marker
            block_end_match = BLOCK_END_REGEX.search(line)
            if block_end_match and in_block:
                in_block = False

                # Add this line to buffer and add buffer to results
                buffer += line
                result.append(buffer)
                buffer = ""
                continue

            # Add line to buffer
            buffer += line

        # Add remaining buffer
        if buffer:
            result.append(buffer)

        return result

    def clean_conflict(self, path: str) -> bool:
        """Remove conflict markers from a file."""
        conflict_file_path = self._get_conflict_file_path(path)
        repo_file_path = self._get_repo_file_path(path)

        # Check if conflict file exists
        if not os.path.exists(conflict_file_path):
            logger.error(f"Conflict file not found for: {path}")
            return False

        try:
            # Copy conflict file to repo file
            shutil.copy2(conflict_file_path, repo_file_path)

            # Remove conflict file
            os.remove(conflict_file_path)

            # Remove parent directories if empty
            parent_dir = os.path.dirname(conflict_file_path)
            while parent_dir != self.conflict_path:
                if not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    parent_dir = os.path.dirname(parent_dir)
                else:
                    break

            return True
        except Exception as e:
            logger.error(f"Error cleaning conflict: {e}")
            return False


# Create a global instance for use throughout the application
conflict_manager = ConflictManager()
