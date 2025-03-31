from typing import List, Dict, Optional, Tuple, TypeAlias
import os
import json
from enum import Enum
from fs_utils import hook

USERPATH = os.path.expanduser("~")
SYSTEMPATH = "/"


class FileType(Enum):
    USER = 0
    SYSTEM = 1


Owner: TypeAlias = str


class Path:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Path {path} does not exist.")
        if os.path.samefile(self.path, USERPATH) or os.path.samefile(
            self.path, SYSTEMPATH
        ):
            raise ValueError("Path cannot be ~ or /")
        self.type = FileType.USER if self.path.startswith(USERPATH) else FileType.SYSTEM
        self.relative_path = (
            os.path.relpath(self.path, USERPATH)
            if self.type == FileType.USER
            else os.path.relpath(self.path, SYSTEMPATH)
        )
        self.is_dir = os.path.isdir(self.path)
        self.cut_path = self._normalize_path(self.relative_path.split(os.sep))
        self.name = self.cut_path[-1] if self.cut_path else ""

    def _normalize_path(self, parts: List[str]) -> List[str]:
        return [p for p in parts if p]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Path):
            return os.path.samefile(self.path, other.path)
        return False


class Node:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name

    def is_proper_subtree_of(self, other: Path) -> bool:
        other_parts = other.cut_path
        self_parts = self.path.cut_path
        return (
            len(self_parts) > len(other_parts)
            and self_parts[: len(other_parts)] == other_parts
        )


class File(Node):
    def __init__(self, path: Path):
        if path.is_dir:
            raise ValueError("File cannot be initialized with directory path")
        super().__init__(path)


class Dir(Node):
    def __init__(self, path: Path, auto_fill: bool = True):
        if not path.is_dir:
            raise ValueError("Dir requires a directory path")
        super().__init__(path)
        self.subdirs: Dict[str, Dir] = {}
        self.files: Dict[str, File] = {}
        if auto_fill:
            self._fill_contents()

    def _fill_contents(self) -> None:
        try:
            for name in os.listdir(self.path.path):
                full_path = os.path.join(self.path.path, name)
                path = Path(full_path)
                if path.is_dir:
                    self.subdirs[name] = Dir(path)
                else:
                    self.files[name] = File(path)
        except PermissionError:
            raise ValueError(f"Permission denied for path: {self.path.path}")


def merge_two_trees_dir(source: Dir, target: Dir) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    if not source.is_proper_subtree_of(target.path):
        raise ValueError("Source is not a proper subtree of target")

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            raise ValueError(f"Missing directory in path: {part}")
        current_dir = current_dir.subdirs[part]

    current_dir.subdirs[source.name] = source


def merge_two_trees_file(source: File, target: Dir) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    if not source.is_proper_subtree_of(target.path):
        raise ValueError("Source is not a proper subtree of target")

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            raise ValueError(f"Missing directory in path: {part}")
        current_dir = current_dir.subdirs[part]

    current_dir.files[source.name] = source


class FileSystem:
    def __init__(self, if_hook: bool = False):
        self.forest: Tuple[
            Tuple[List[Tuple[Dir, Owner]], List[Tuple[File, Owner]]],
            Tuple[List[Tuple[Dir, Owner]], List[Tuple[File, Owner]]],
        ] = (([], []), ([], []))
        self.if_hook = if_hook

    def add(self, path_str: str, owner: Owner) -> None:
        new_path = Path(path_str)
        isdir = new_path.is_dir
        if isdir:
            new_node = Dir(new_path)
            dir_wait_for_merge_to: List[Tuple[Dir, Owner]] = []
            file_wait_for_merge_to: List[Tuple[File, Owner]] = []
            for existing_top_dir in self.forest[new_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                existing_owner = existing_top_dir[1]
                if new_node.path == existing_top_tree.path:
                    raise ValueError(f"Path {new_path.path} already exists")
                if new_node.is_proper_subtree_of(existing_top_tree.path):
                    if existing_owner == owner:
                        merge_two_trees_dir(new_node, existing_top_tree)
                        if self.if_hook:
                            hook(
                                f"Merge directory {new_path.path} into {existing_top_tree.path.path}"
                            )
                        return
                    else:
                        raise ValueError(
                            f"There exists a super directory of {path_str} with a different owner: {existing_owner}"
                        )
                if existing_top_tree.is_proper_subtree_of(new_node.path):
                    if existing_owner == owner:
                        dir_wait_for_merge_to.append(existing_top_dir)
                    else:
                        raise ValueError(
                            f"There exists a sub directory of {path_str} with a different owner: {existing_owner}"
                        )
            for existing_top_file in self.forest[new_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                existing_owner = existing_top_file[1]
                if existing_top_tree.is_proper_subtree_of(new_node.path):
                    if existing_owner == owner:
                        file_wait_for_merge_to.append(existing_top_file)
                    else:
                        raise ValueError(
                            f"There exists a sub directory of {path_str} with a different owner: {existing_owner}"
                        )
            for existing_top_tree in dir_wait_for_merge_to:
                merge_two_trees_dir(existing_top_tree[0], new_node)
            for existing_top_tree in file_wait_for_merge_to:
                merge_two_trees_file(existing_top_tree[0], new_node)
            # remove the existing top trees after merging to make add atomic
            for existing_top_tree in dir_wait_for_merge_to:
                self.forest[new_path.type.value][0].remove(existing_top_tree)
            for existing_top_tree in file_wait_for_merge_to:
                self.forest[new_path.type.value][1].remove(existing_top_tree)
            self.forest[new_path.type.value][0].append((new_node, owner))
            if self.if_hook:
                hook(
                    f"Add a top directory {new_node.path.path} merged with dir:{[existing_top_tree[0].path.path for existing_top_tree in dir_wait_for_merge_to]} and file:{[existing_top_tree[0].path.path for existing_top_tree in file_wait_for_merge_to]} with owner {owner}"
                )
        else:
            new_node = File(new_path)
            for existing_top_file in self.forest[new_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                existing_owner = existing_top_file[1]
                if new_node.path == existing_top_tree.path:
                    raise ValueError(f"Path {new_path.path} already exists")
            for existing_top_dir in self.forest[new_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                existing_owner = existing_top_dir[1]
                if new_node.is_proper_subtree_of(existing_top_tree.path):
                    if existing_owner == owner:
                        merge_two_trees_file(new_node, existing_top_tree)
                        if self.if_hook:
                            hook(
                                f"Merge file {new_path.path} into {existing_top_tree.path.path}"
                            )
                        return
            self.forest[new_path.type.value][1].append((new_node, owner))
            if self.if_hook:
                hook(f"Add a top file {new_node.path.path} with owner {owner}")

    def remove(self, path_str: str) -> None:
        target_path = Path(path_str)
        isdir = target_path.is_dir
        if isdir:
            for existing_top_dir in self.forest[target_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][0].remove(existing_top_dir)
                    if self.if_hook:
                        hook(f"Remove top directory {target_path.path}")
                    return
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    if parent:
                        name = target_path.name
                        self._remove_from_parent(parent, name, isdir)
                        if self.if_hook:
                            hook(
                                f"Remove directory {target_path.path} from {parent.path.path}"
                            )
                        return
            raise ValueError(f"Path not found: {path_str}")
        else:
            for existing_top_file in self.forest[target_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][1].remove(existing_top_file)
                    if self.if_hook:
                        hook(f"Remove top file {target_path.path}")
                    return
            for existing_top_tree, _ in self.forest[target_path.type.value][0]:
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    if parent:
                        name = target_path.name
                        self._remove_from_parent(parent, name, isdir)
                        if self.if_hook:
                            hook(
                                f"Remove file {target_path.path} from {parent.path.path}"
                            )
                        return
            raise ValueError(f"Path not found: {path_str}")

    def _find_parent_dir(self, root: Dir, target: Path) -> Optional[Dir]:
        current = root
        for part in target.cut_path[len(root.path.cut_path) : -1]:
            if part not in current.subdirs:
                raise ValueError(f"Path not found: {target.path}")
            current = current.subdirs[part]
        return current

    def _remove_from_parent(self, parent: Dir, name: str, isdir: bool) -> None:
        if isdir and name in parent.subdirs:
            del parent.subdirs[name]
        elif not isdir and name in parent.files:
            del parent.files[name]
        else:
            raise ValueError("Target not found in parent directory")

    @staticmethod
    def _serialize_node_dir(node: Dir, full_path: bool = False) -> Dict:
        name = node.path.relative_path if full_path else node.name
        return {
            "name": name,
            "subdirs": [
                FileSystem._serialize_node_dir(d) for d in node.subdirs.values()
            ],
            "files": [FileSystem._serialize_node_file(f) for f in node.files.values()],
        }

    @staticmethod
    def _serialize_node_file(node: File, full_path: bool = False) -> Dict:
        name = node.path.relative_path if full_path else node.name
        return {"name": name}

    def to_json(self) -> str:
        dict_ = {
            "USER": {
                "top_dirs": [
                    {"tree": self._serialize_node_dir(node[0], True), "owner": node[1]}
                    for node in self.forest[0][0]
                ],
                "top_files": [
                    {"tree": self._serialize_node_file(node[0], True), "owner": node[1]}
                    for node in self.forest[0][1]
                ],
            },
            "SYSTEM": {
                "top_dirs": [
                    {"tree": self._serialize_node_dir(node[0], True), "owner": node[1]}
                    for node in self.forest[1][0]
                ],
                "top_files": [
                    {"tree": self._serialize_node_file(node[0], True), "owner": node[1]}
                    for node in self.forest[1][1]
                ],
            },
        }
        return json.dumps(dict_, indent=2)

    @staticmethod
    def _deserialize_dir_node(data: Dict, parent_path: str = "") -> Dir:
        full_path = os.path.join(parent_path, data["name"])
        path = Path(full_path)

        node = Dir(path, False)
        for subdir in data.get("subdirs", []):
            child = FileSystem._deserialize_dir_node(subdir, full_path)
            node.subdirs[child.name] = child
        for file in data.get("files", []):
            child = FileSystem._deserialize_file_node(file, full_path)
            node.files[child.name] = child
        return node

    @staticmethod
    def _deserialize_file_node(data: Dict, parent_path: str = "") -> File:
        full_path = os.path.join(parent_path, data["name"])
        path = Path(full_path)
        return File(path)

    @classmethod
    def from_json(cls, json_str: str) -> "FileSystem":
        fs = FileSystem()
        fs.forest = (([], []), ([], []))
        data = json.loads(json_str)
        for top_dir in data["USER"].get("top_dirs", []):
            node = cls._deserialize_dir_node(top_dir["tree"], USERPATH)
            fs.forest[0][0].append((node, top_dir["owner"]))
        for top_file in data["USER"].get("top_files", []):
            node = cls._deserialize_file_node(top_file["tree"], USERPATH)
            fs.forest[0][1].append((node, top_file["owner"]))
        for top_dir in data["SYSTEM"].get("top_dirs", []):
            node = cls._deserialize_dir_node(top_dir["tree"], SYSTEMPATH)
            fs.forest[1][0].append((node, top_dir["owner"]))
        for top_file in data["SYSTEM"].get("top_files", []):
            node = cls._deserialize_file_node(top_file["tree"], SYSTEMPATH)
            fs.forest[1][1].append((node, top_file["owner"]))
        return fs

    def __repr__(self) -> str:
        return self.to_json()


if __name__ == "__main__":
    fs = FileSystem(if_hook=True)
    fs.add("/etc/keyd", "keyd")
    fs.add("/etc/kmscon", "kmscon")
    fs.add("~/.zshrc", "zsh")
    fs.add("~/.config/nvim/lua", "nvim")
    fs.remove("~/.config/nvim/lua/lualine/themes/ras.lua")
    fs.remove("~/.config/nvim/lua/lualine/")
    fs.add("~/.config/nvim", "nvim")
    json_str = fs.to_json()
    load_fs = FileSystem.from_json(json_str)
    print(load_fs.to_json() == json_str)
