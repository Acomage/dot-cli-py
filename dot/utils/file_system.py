import os
import pathlib
from typing import List, Dict, Union, Optional, Any, Tuple


class Node:
    """Base class for file system nodes."""

    def __init__(self, name: str, owner: str):
        if " " in name:
            raise ValueError(f"Node name cannot contain spaces: {name}")

        self.name = name
        self.owner = owner

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        result = {"name": self.name, "owner": self.owner}
        return result


class File(Node):
    """Represents a file in the file system."""

    def __init__(self, name: str, owner: str):
        if "/" in name:
            raise ValueError(f"File name cannot contain '/': {name}")
        super().__init__(name, owner)

    def to_dict(self) -> Dict[str, Any]:
        return super().to_dict()


class Dir(Node):
    """Represents a directory in the file system."""

    def __init__(
        self, name: str, owner: str, contents: Optional[List[Union["Dir", File]]] = None
    ):
        if "/" in name and not self._is_valid_root_name(name):
            raise ValueError(
                f"Directory name cannot contain '/' unless it's a root node: {name}"
            )
        super().__init__(name, owner)
        self.contents = contents or []

    @staticmethod
    def _is_valid_root_name(name: str) -> bool:
        """Check if a name is valid for a root node."""
        # Root nodes can have slashes but should follow a path structure
        parts = name.split("/")
        return all(part and " " not in part for part in parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert directory to dictionary representation."""
        result = super().to_dict()
        if self.contents:
            result["contents"] = [item.to_dict() for item in self.contents]
        return result

    def find_node(self, name: str) -> Optional[Union["Dir", File]]:
        """Find a node with the given name in the contents."""
        for node in self.contents:
            if node.name == name:
                return node
        return None

    def add_node(self, node: Union["Dir", File]) -> None:
        """Add a node to the contents."""
        existing = self.find_node(node.name)
        if existing:
            if isinstance(existing, Dir) and isinstance(node, Dir):
                # Merge directories with the same name if they have the same owner
                if existing.owner != node.owner:
                    raise ValueError(
                        f"Directory '{node.name}' already exists with different owner"
                    )
                # Merge contents
                for child in node.contents:
                    existing.add_node(child)
            else:
                raise ValueError(f"Node with name '{node.name}' already exists")
        else:
            self.contents.append(node)

    def remove_node(self, name: str) -> Optional[Union["Dir", File]]:
        """Remove a node from the contents and return it."""
        for i, node in enumerate(self.contents):
            if node.name == name:
                return self.contents.pop(i)
        return None


class FileSystem:
    """File indexing system to manage marked files in the real file system."""

    def __init__(self):
        self.USER_PATH = str(pathlib.Path.home()) + "/"
        self.SYSTEM_PATH = "/"
        self.forests = {
            "USER": [],  # List of root nodes in USER forest
            "SYSTEM": [],  # List of root nodes in SYSTEM forest
        }

    def _normalize_path(self, path: str) -> str:
        """Normalize path, expanding ~ to user's home directory."""
        if path.startswith("~"):
            path = str(pathlib.Path.home()) + path[1:]
        return os.path.normpath(path)

    def _get_forest_type(self, path: str) -> str:
        """Determine which forest a path belongs to."""
        normalized = self._normalize_path(path)
        if normalized.startswith(str(pathlib.Path.home())):
            return "USER"
        elif normalized.startswith("/"):
            return "SYSTEM"
        else:
            raise ValueError(f"Invalid path: {path}")

    def _get_relative_path(self, path: str) -> str:
        """Get path relative to the forest root."""
        normalized = self._normalize_path(path)
        forest_type = self._get_forest_type(path)

        if forest_type == "USER":
            home = str(pathlib.Path.home())
            if normalized == home:
                return ""
            return normalized[len(home) + 1 :]  # +1 to remove the trailing slash
        else:  # SYSTEM
            if normalized == "/":
                return ""
            return normalized[1:]  # Remove leading slash

    def _find_best_root_match(
        self, rel_path: str, forest_type: str
    ) -> Tuple[Optional[Dir], str]:
        """
        Find the best matching root node for a given relative path.
        Returns (root_node, remaining_path)
        """
        if not rel_path:
            return None, ""

        best_match = None
        best_match_len = 0
        remaining = rel_path

        # First look for exact matches
        for root in self.forests[forest_type]:
            if root.name == rel_path:
                return root, ""

        # Then look for path-style roots that are part of the path
        path_parts = rel_path.split("/")

        for root in self.forests[forest_type]:
            if "/" in root.name:
                # This is a path-style root
                root_parts = root.name.split("/")

                # Check if this root is a prefix of our path
                if len(root_parts) <= len(path_parts):
                    match = True
                    for i, part in enumerate(root_parts):
                        if part != path_parts[i]:
                            match = False
                            break

                    if match and len(root_parts) > best_match_len:
                        best_match = root
                        best_match_len = len(root_parts)
                        remaining = "/".join(path_parts[len(root_parts) :])
            else:
                # Single-component root
                if root.name == path_parts[0] and 1 > best_match_len:
                    best_match = root
                    best_match_len = 1
                    remaining = "/".join(path_parts[1:])

        return best_match, remaining

    def _find_node_by_path(
        self, path: str
    ) -> Tuple[Optional[Dir], Optional[Union[Dir, File]], str]:
        """
        Find a node by its path.
        Returns (parent_dir, node, remaining_path)
        """
        forest_type = self._get_forest_type(path)
        rel_path = self._get_relative_path(path)

        # Empty path
        if not rel_path:
            return None, None, ""

        # Find the best matching root
        root_node, remaining = self._find_best_root_match(rel_path, forest_type)

        if not root_node:
            return None, None, rel_path

        # If no remaining path or root isn't a directory, return the root
        if not remaining or not isinstance(root_node, Dir):
            return None, root_node, remaining

        # Navigate through the tree
        current = root_node
        parent = None
        parts = remaining.split("/")

        for i, part in enumerate(parts):
            if not part:  # Skip empty parts
                continue

            if not isinstance(current, Dir):
                # Can't navigate into a file
                return parent, current, "/".join(parts[i:])

            next_node = current.find_node(part)
            if not next_node:
                # Path doesn't exist further
                return current, None, "/".join(parts[i:])

            parent = current
            current = next_node

        return parent, current, ""

    def _scan_directory(self, path: str, owner: str) -> Dir:
        """Scan a directory and create a Dir node with its contents."""
        real_path = self._normalize_path(path)
        if not os.path.exists(real_path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        if not os.path.isdir(real_path):
            raise NotADirectoryError(f"Path is not a directory: {path}")

        dir_name = os.path.basename(real_path) or real_path
        dir_node = Dir(dir_name, owner)

        for item in os.listdir(real_path):
            item_path = os.path.join(real_path, item)

            if os.path.isdir(item_path):
                # Recursively scan subdirectories
                subdir = self._scan_directory(item_path, owner)
                dir_node.add_node(subdir)
            else:
                # Add files
                file_node = File(item, owner)
                dir_node.add_node(file_node)

        return dir_node

    def add(self, path: str, owner: str) -> None:
        """Add a path to the appropriate forest with the given owner."""
        real_path = self._normalize_path(path)
        if not os.path.exists(real_path):
            raise FileNotFoundError(f"Path does not exist: {path}")

        forest_type = self._get_forest_type(path)
        rel_path = self._get_relative_path(path)

        # Check for existing subtrees in this new path
        existing_subtrees = []
        for root in list(self.forests[forest_type]):
            if root.name.startswith(rel_path + "/"):
                # This is a subtree of the path we're adding
                if root.owner != owner:
                    raise ValueError(
                        f"Cannot add '{path}' with owner '{owner}' - conflicts with existing subtree owned by '{root.owner}'"
                    )
                existing_subtrees.append(root)
                self.forests[forest_type].remove(root)

        # For directories, scan them with the actual directory structure
        if os.path.isdir(real_path):
            # Create new directory tree
            dir_node = self._scan_directory(real_path, owner)
            dir_node.name = rel_path

            # Find existing trees that should contain this path
            parent_path = os.path.dirname(rel_path)
            if parent_path:
                parent_rel_path = parent_path
                parent, _, _ = self._find_node_by_path(
                    f"~/{parent_rel_path}"
                    if forest_type == "USER"
                    else f"/{parent_rel_path}"
                )

                if parent and isinstance(parent, Dir) and parent.owner == owner:
                    # This new directory should be added to an existing parent
                    parent.add_node(dir_node)
                    return

            # Add to forest as a root node
            self.forests[forest_type].append(dir_node)

            # Reintegrate any existing subtrees we removed
            for subtree in existing_subtrees:
                # Get the relative path from our new tree to the subtree
                subtree_rel_path = subtree.name[len(rel_path) + 1 :]

                # Find the parent node where this subtree should be placed
                current = dir_node
                path_parts = subtree_rel_path.split("/")

                # Navigate to the correct insertion point
                for _, part in enumerate(path_parts[:-1]):
                    next_node = current.find_node(part)
                    if not next_node or not isinstance(next_node, Dir):
                        # Create intermediate directories if needed
                        new_dir = Dir(part, owner)
                        current.add_node(new_dir)
                        current = new_dir
                    else:
                        current = next_node

                # Remove the last component which is the subtree root name
                existing_node = current.find_node(path_parts[-1])
                if existing_node:
                    current.remove_node(path_parts[-1])

                # Adjust subtree name to just the leaf component
                subtree.name = path_parts[-1]

                # Add the subtree at the correct location
                current.add_node(subtree)
        else:
            # For regular files
            file_node = File(os.path.basename(real_path), owner)

            # Check if this file should be placed inside an existing directory
            dir_path = os.path.dirname(rel_path)
            if dir_path:
                dir_rel_path = dir_path
                parent, _, _ = self._find_node_by_path(
                    f"~/{dir_rel_path}" if forest_type == "USER" else f"/{dir_rel_path}"
                )

                if parent and isinstance(parent, Dir):
                    parent.add_node(file_node)
                    return

            # Add as a root file node
            file_node.name = rel_path
            self.forests[forest_type].append(file_node)

    def remove(self, path: str) -> None:
        """Remove a path from the appropriate forest."""
        parent, node, remaining = self._find_node_by_path(path)

        if not node or remaining:
            raise ValueError(f"Path not found: {path}")

        if parent:
            parent.remove_node(node.name)
        else:
            # It's a root node
            forest_type = self._get_forest_type(path)
            self.forests[forest_type].remove(node)

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        """Convert the forests to dictionary representation."""
        return {
            "USER": [node.to_dict() for node in self.forests["USER"]],
            "SYSTEM": [node.to_dict() for node in self.forests["SYSTEM"]],
        }

    def to_json(self) -> str:
        """Convert the forests to JSON representation."""
        import json

        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, List[Dict[str, Any]]]) -> "FileSystem":
        """Create a FileSystem from a dictionary representation."""
        fs = cls()

        # Process USER forest
        if "USER" in data:
            for node_dict in data["USER"]:
                fs.forests["USER"].append(cls._create_node_from_dict(node_dict))

        # Process SYSTEM forest
        if "SYSTEM" in data:
            for node_dict in data["SYSTEM"]:
                fs.forests["SYSTEM"].append(cls._create_node_from_dict(node_dict))

        return fs

    @classmethod
    def _create_node_from_dict(cls, node_dict: Dict[str, Any]) -> Union[Dir, File]:
        """Create a node (Dir or File) from a dictionary representation."""
        name = node_dict.get("name", "")
        owner = node_dict.get("owner", "")

        if "contents" in node_dict:
            # This is a directory
            dir_node = Dir(name, owner)

            # Process contents
            for child_dict in node_dict.get("contents", []):
                child_node = cls._create_node_from_dict(child_dict)
                dir_node.add_node(child_node)

            return dir_node
        else:
            # This is a file
            return File(name, owner)

    @classmethod
    def from_json(cls, json_str: str) -> "FileSystem":
        """Create a FileSystem from a JSON string representation."""
        import json

        data = json.loads(json_str)
        return cls.from_dict(data)


if __name__ == "__main__":
    fs = FileSystem()
    fs.add("~/.zshrc", "zsh")
    fs.add("~/.config/nvim/lua", "nvim")
    fs.add("~/.config/nvim", "nvim")
    fs.add("/etc/keyd", "keyd")

    json_str = fs.to_json()
    loaded_fs = FileSystem.from_json(json_str)
    print(json_str == loaded_fs.to_json())
