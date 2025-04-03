from typing import List, Dict, Tuple
import os
import json

from rewrite_by_hand.utils.hook import Hooker
from rewrite_by_hand.data.variables import USERPATH, SYSTEMPATH
from rewrite_by_hand.utils.fs_type import Path, File, Dir, Owner


def merge_two_trees_dir(source: Dir, target: Dir) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    if not source.is_proper_subtree_of(target.path):
        raise ValueError("Source is not a proper subtree of target")

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            current_dir.subdirs[part] = Dir(
                Path(os.path.join(current_dir.path.path, part)), auto_fill=False
            )
        current_dir = current_dir.subdirs[part]

    current_dir.subdirs[source.name] = source


def add_file_to_dir(source: File, target: Dir) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    if not source.is_proper_subtree_of(target.path):
        raise ValueError("Source is not a proper subtree of target")

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            current_dir.subdirs[part] = Dir(
                Path(os.path.join(current_dir.path.path, part)), auto_fill=False
            )
        current_dir = current_dir.subdirs[part]
    if source.name in current_dir.files:
        raise ValueError(
            f"File {source.path.path} already exists in {current_dir.path.path}"
        )
    current_dir.files[source.name] = source


class FileSystem:
    def __init__(self, if_hook: bool = False):
        self.forest: Tuple[
            Tuple[
                List[Tuple[Dir, Owner]],
                List[Tuple[File, Owner]],
            ],
            Tuple[
                List[Tuple[Dir, Owner]],
                List[Tuple[File, Owner]],
            ],
        ] = (([], []), ([], []))
        self.if_hook = if_hook
        if if_hook:
            self.hooker = Hooker()

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
                            self.hooker.add_dir(new_node.path, [])
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
            # do not need to merge file trees, because they are already there
            # for existing_top_tree in file_wait_for_merge_to:
            #     merge_two_trees_file(existing_top_tree[0], new_node)
            # remove the existing top trees after merging to make add atomic
            for existing_top_tree in dir_wait_for_merge_to:
                self.forest[new_path.type.value][0].remove(existing_top_tree)
            for existing_top_tree in file_wait_for_merge_to:
                self.forest[new_path.type.value][1].remove(existing_top_tree)
            self.forest[new_path.type.value][0].append((new_node, owner))
            if self.if_hook:
                self.hooker.add_dir(
                    new_node.path, [dir[0] for dir in dir_wait_for_merge_to]
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
                        add_file_to_dir(new_node, existing_top_tree)
                        if self.if_hook:
                            self.hooker.add_file(new_node.path)
                        return
                    else:
                        raise ValueError(
                            f"There exists a super directory of {path_str} with a different owner: {existing_owner}"
                        )
            self.forest[new_path.type.value][1].append((new_node, owner))
            if self.if_hook:
                self.hooker.add_file(new_node.path)

    def remove(self, path_str: str) -> None:
        target_path = Path(path_str)
        isdir = target_path.is_dir
        if isdir:
            for existing_top_dir in self.forest[target_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][0].remove(existing_top_dir)
                    if self.if_hook:
                        self.hooker.remove(target_path)
                    return
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    name = target_path.name
                    self._remove_from_parent(parent, name, isdir)
                    if self.if_hook:
                        self.hooker.remove(target_path)
                    return
            raise ValueError(f"Path not found: {path_str}")
        else:
            for existing_top_file in self.forest[target_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][1].remove(existing_top_file)
                    if self.if_hook:
                        self.hooker.remove(target_path)
                    return
            for existing_top_tree, _ in self.forest[target_path.type.value][0]:
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    name = target_path.name
                    self._remove_from_parent(parent, name, isdir)
                    if self.if_hook:
                        self.hooker.remove(target_path)
                    return
            raise ValueError(f"Path not found: {path_str}")

    def add_conflict(self, path_str: str) -> None:
        target_path = Path(path_str)
        if target_path.is_dir:
            raise ValueError("Cannot add a conflict directory, only files are allowed")
        else:
            for existing_top_tree, _ in self.forest[target_path.type.value][1]:
                if target_path.path == existing_top_tree.path:
                    if existing_top_tree.conflict:
                        raise ValueError(
                            f"File {path_str} already has a conflict version"
                        )
                    existing_top_tree.conflict = True
                    # TODO: add hook
                    return
            for existing_top_tree, _ in self.forest[target_path.type.value][0]:
                if target_path.is_proper_subtree_of(existing_top_tree.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    if target_path.name in parent.files:
                        if parent.files[target_path.name].conflict:
                            raise ValueError(
                                f"File {path_str} already has a conflict version"
                            )
                        parent.files[target_path.name].conflict = True
                        # TODO: add hook
                        return
            raise ValueError(f"File {path_str} is not managed")

    def remove_conflict(self, path_str: str) -> None:
        target_path = Path(path_str)
        if target_path.is_dir:
            raise ValueError(
                "Cannot add a conflict directory, only files are allowed, so you cannot remove it"
            )
        else:
            for existing_top_tree, _ in self.forest[target_path.type.value][1]:
                if target_path.path == existing_top_tree.path:
                    if not existing_top_tree.conflict:
                        raise ValueError(
                            f"File {path_str} does not have a conflict version"
                        )
                    existing_top_tree.conflict = False
                    # TODO: add hook
                    return
            for existing_top_tree, _ in self.forest[target_path.type.value][0]:
                if target_path.is_proper_subtree_of(existing_top_tree.path):
                    parent = self._find_parent_dir(existing_top_tree, target_path)
                    if target_path.name in parent.files:
                        if not parent.files[target_path.name].conflict:
                            raise ValueError(
                                f"File {path_str} does not have a conflict version"
                            )
                        parent.files[target_path.name].conflict = False
                        # TODO: add hook
                        return
            raise ValueError(f"File {path_str} is not managed")

    def _find_parent_dir(self, root: Dir, target: Path) -> Dir:
        current = root
        for part in target.cut_path[len(root.path.cut_path) : -1]:
            if part not in current.subdirs:
                raise ValueError(
                    f"Path {target.path} not found in existing top directorys"
                )
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
        return {"name": name, "conflict": node.conflict}

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
        return File(path, data["conflict"])

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
    fs = FileSystem(if_hook=False)
    fs.add("/etc/keyd", "keyd")
    fs.add("/etc/kmscon", "kmscon")
    fs.add("~/.zshrc", "zsh")
    fs.add("~/.config/nvim/lua/", "nvim")
    fs.remove("~/.config/nvim/lua/lualine/themes/ras.lua")
    fs.remove("~/.config/nvim/lua/lualine")
    fs.add("~/.config/nvim", "nvim")
    print(fs)
    json_str = fs.to_json()
    loaded_fs = FileSystem.from_json(json_str)
    print(loaded_fs.to_json() == json_str)
