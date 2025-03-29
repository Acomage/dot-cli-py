"""Configuration management for the Dot CLI tool."""

import json
import os
from typing import Dict, List, Any, Optional, Set, Union

from dot.utils.file_system import FileSystem, Dir, File
from dot.utils.logger import logger


class ConfigManager:
    """Manage configuration files for the Dot CLI tool."""

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        self.dotfiles_path = os.path.expanduser("~/.dotfiles")
        self.config_path = os.path.join(self.dotfiles_path, "config.json")
        self.local_config_path = os.path.join(self.dotfiles_path, "local_config.json")

        # Ensure paths exist
        # if not os.path.exists(self.dotfiles_path):
        #     os.makedirs(self.dotfiles_path, exist_ok=True)

        # Initialize file system objects
        self.fs = FileSystem()
        self.local_fs = FileSystem()

        # Load configurations
        self._load_config()
        self._load_local_config()

    def _load_config(self) -> None:
        """Load the global configuration file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    self.fs = FileSystem.from_dict(config_data.get("file_system", {}))
                    self.conflict_files = set(config_data.get("conflict_files", []))
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error loading config file: {e}")
                self.fs = FileSystem()
                self.conflict_files = set()
        else:
            self.fs = FileSystem()
            self.conflict_files = set()

    def _load_local_config(self) -> None:
        """Load the local configuration file."""
        if os.path.exists(self.local_config_path):
            try:
                with open(self.local_config_path, "r", encoding="utf-8") as f:
                    local_config_data = json.load(f)
                    self.local_fs = FileSystem.from_dict(
                        local_config_data.get("file_system", {})
                    )
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error loading local config file: {e}")
                self.local_fs = FileSystem()
        else:
            self.local_fs = FileSystem()

    def save_config(self) -> None:
        """Save the global configuration file."""
        config_data = {
            "file_system": self.fs.to_dict(),
            "conflict_files": list(self.conflict_files),
        }

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2)
        except (OSError, ValueError) as e:
            logger.error(f"Error saving config file: {e}")

    def save_local_config(self) -> None:
        """Save the local configuration file."""
        local_config_data = {
            "file_system": self.local_fs.to_dict(),
        }

        try:
            with open(self.local_config_path, "w", encoding="utf-8") as f:
                json.dump(local_config_data, f, indent=2)
        except (OSError, ValueError) as e:
            logger.error(f"Error saving local config file: {e}")

    def add_file(self, path: str, software: str) -> None:
        """Add a file to the configuration."""
        real_path = os.path.expanduser(path)
        if not os.path.exists(real_path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        # Add to the global file system
        self.fs.add(real_path, software)

        # Add to the local file system
        self.local_fs.add(real_path, software)

        # Save configurations
        self.save_config()
        self.save_local_config()

    def remove_file(self, path: str, software: str) -> None:
        """Remove a file from the configuration."""
        real_path = os.path.expanduser(path)

        # Check if the file is in the configuration
        try:
            # Remove from the global file system
            self.fs.remove(real_path)

            # Remove from the local file system
            self.local_fs.remove(real_path)

            # Remove from conflict files if present
            normalized_path = os.path.normpath(real_path)
            if normalized_path in self.conflict_files:
                self.conflict_files.remove(normalized_path)

            # Save configurations
            self.save_config()
            self.save_local_config()
        except ValueError as e:
            logger.error(f"Error removing file: {e}")
            raise

    def mark_as_conflict(self, path: str) -> None:
        """Mark a file as having conflicts."""
        real_path = os.path.expanduser(path)
        normalized_path = os.path.normpath(real_path)

        self.conflict_files.add(normalized_path)
        self.save_config()

    def unmark_as_conflict(self, path: str) -> None:
        """Unmark a file as having conflicts."""
        real_path = os.path.expanduser(path)
        normalized_path = os.path.normpath(real_path)

        if normalized_path in self.conflict_files:
            self.conflict_files.remove(normalized_path)
            self.save_config()

    def is_conflict(self, path: str) -> bool:
        """Check if a file is marked as having conflicts."""
        real_path = os.path.expanduser(path)
        normalized_path = os.path.normpath(real_path)

        return normalized_path in self.conflict_files

    def manage_software(self, software: str) -> None:
        """Add software configuration to local config."""
        # Find nodes in global config with the given owner
        global_nodes = self._find_nodes_by_owner(self.fs, software)

        # Add these nodes to the local config
        for node in global_nodes:
            if isinstance(node, Dir):
                self.local_fs.add(os.path.join("/", node.name), software)
            elif isinstance(node, File):
                self.local_fs.add(os.path.join("/", node.name), software)

        self.save_local_config()

    def _find_nodes_by_owner(
        self, fs: FileSystem, owner: str
    ) -> List[Union[Dir, File]]:
        """Find all nodes with the given owner in the filesystem."""
        nodes = []

        for forest_type in ["USER", "SYSTEM"]:
            for node in fs.forests[forest_type]:
                if node.owner == owner:
                    nodes.append(node)

        return nodes


# Create a global instance for use throughout the application
config_manager = ConfigManager()
