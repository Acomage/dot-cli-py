from typing import List, Dict, Tuple, Union
import os
import json
import sys
from typing_extensions import Literal

from rewrite_by_hand.utils.hook import Hooker
from rewrite_by_hand.data.variables import USERPATH, SYSTEMPATH
from rewrite_by_hand.utils.fs_type import Path, File, Dir, Owner
from rewrite_by_hand.cli.output import output_manager


def merge_two_trees_dir(source: Dir, target: Dir) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            current_dir.subdirs[part] = Dir(
                Path(os.path.join(current_dir.path.path, part)), auto_fill=False
            )
        current_dir = current_dir.subdirs[part]

    current_dir.subdirs[source.name] = source


def add_file_to_dir(source: File, target: Dir, local: bool = False) -> None:
    target_parts = target.path.cut_path
    source_parts = source.path.cut_path

    current_dir = target
    for part in source_parts[len(target_parts) : -1]:
        if part not in current_dir.subdirs:
            current_dir.subdirs[part] = Dir(
                Path(os.path.join(current_dir.path.path, part)), auto_fill=False
            )
        current_dir = current_dir.subdirs[part]
    if source.name in current_dir.files:
        if local:
            output_manager.err("File_Already_Managed", path=source.path.path)
        else:
            output_manager.err("File_Already_Exists", path=source.path.path)
        sys.exit(1)
    current_dir.files[source.name] = source


class FileSystem:
    def __init__(self, if_hook: bool = False, local: bool = False) -> None:
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
        self.local = local
        self.if_hook = if_hook
        if if_hook:
            self.hooker = Hooker()

    def add(self, path_str: str, owner: Owner, if_hook: bool = True) -> None:
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
                    if self.local:
                        output_manager.err("File_Already_Managed", path=new_path.path)
                    else:
                        output_manager.err("File_Already_Exists", path=new_path.path)
                    sys.exit(1)
                if new_node.is_proper_subtree_of(existing_top_tree.path):
                    if existing_owner == owner:
                        merge_two_trees_dir(new_node, existing_top_tree)
                        if self.if_hook and if_hook:
                            self.hooker.add_dir(new_node.path, [])
                        return
                    else:
                        output_manager.err(
                            "Super_Dir_With_Differnet_Owner",
                            path=new_path.path,
                            owner=existing_owner,
                        )
                        sys.exit(1)
                if existing_top_tree.is_proper_subtree_of(new_node.path):
                    if existing_owner == owner:
                        dir_wait_for_merge_to.append(existing_top_dir)
                    else:
                        output_manager.err(
                            "Sub_Dir_With_Different_Owner",
                            path=new_path.path,
                            owner=existing_owner,
                        )
                        sys.exit(1)
            for existing_top_file in self.forest[new_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                existing_owner = existing_top_file[1]
                if existing_top_tree.is_proper_subtree_of(new_node.path):
                    if existing_owner == owner:
                        file_wait_for_merge_to.append(existing_top_file)
                    else:
                        output_manager.err(
                            "Sub_File_With_Different_Owner",
                            path=new_path.path,
                            owner=existing_owner,
                        )
                        sys.exit(1)
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
            if self.if_hook and if_hook:
                self.hooker.add_dir(
                    new_node.path, [dir[0] for dir in dir_wait_for_merge_to]
                )
        else:
            new_node = File(new_path)
            for existing_top_file in self.forest[new_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                existing_owner = existing_top_file[1]
                if new_node.path == existing_top_tree.path:
                    if self.local:
                        output_manager.err("File_Already_Managed", path=new_path.path)
                    else:
                        output_manager.err("File_Already_Exists", path=new_path.path)
                    sys.exit(1)
            for existing_top_dir in self.forest[new_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                existing_owner = existing_top_dir[1]
                if new_node.is_proper_subtree_of(existing_top_tree.path):
                    if existing_owner == owner:
                        add_file_to_dir(new_node, existing_top_tree, local=self.local)
                        if self.if_hook and if_hook:
                            self.hooker.add_file(new_node.path)
                        return
                    else:
                        output_manager.err(
                            "Super_Dir_With_Differnet_Owner",
                            path=new_path.path,
                            owner=existing_owner,
                        )
                        sys.exit(1)
            self.forest[new_path.type.value][1].append((new_node, owner))
            if self.if_hook and if_hook:
                self.hooker.add_file(new_node.path)

    def remove(self, path_str: str, if_hook: bool = True) -> None:
        target_path = Path(path_str)
        isdir = target_path.is_dir
        if isdir:
            for existing_top_dir in self.forest[target_path.type.value][0]:
                existing_top_tree = existing_top_dir[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][0].remove(existing_top_dir)
                    if self.if_hook and if_hook:
                        self.hooker.remove_top(target_path)
                    return
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(
                        existing_top_tree, target_path, local=self.local
                    )
                    name = target_path.name
                    self._remove_from_parent(parent, name, isdir, local=self.local)
                    if self.if_hook and if_hook:
                        self.hooker.remove(target_path)
                    return
            output_manager.err("Path_Not_Found", path=target_path.path)
            sys.exit(1)
        else:
            for existing_top_file in self.forest[target_path.type.value][1]:
                existing_top_tree = existing_top_file[0]
                if existing_top_tree.path == target_path:
                    self.forest[target_path.type.value][1].remove(existing_top_file)
                    if self.if_hook and if_hook:
                        self.hooker.remove_top(target_path)
                    return
            for existing_top_tree, _ in self.forest[target_path.type.value][0]:
                if target_path.path.startswith(existing_top_tree.path.path):
                    parent = self._find_parent_dir(
                        existing_top_tree, target_path, local=self.local
                    )
                    name = target_path.name
                    self._remove_from_parent(parent, name, isdir, local=self.local)
                    if self.if_hook and if_hook:
                        self.hooker.remove(target_path)
                    return
            if self.local:
                output_manager.err(
                    "Path_Does_Not_Contain_Local_Config", path=target_path.path
                )
            else:
                output_manager.err("Path_Not_Found", path=target_path.path)
            sys.exit(1)

    def if_exists(
        self, path_str: str
    ) -> Union[Tuple[Literal[True], Owner], Tuple[Literal[False], None]]:
        path = Path(path_str)
        isdir = path.is_dir
        if isdir:
            for existing_top_tree, owner in self.forest[path.type.value][0]:
                if existing_top_tree.path == path:
                    return True, owner
                if path.path.startswith(existing_top_tree.path.path):
                    current = existing_top_tree
                    for part in path.cut_path[len(current.path.cut_path) :]:
                        if part not in current.subdirs:
                            return False, None
                        current = current.subdirs[part]
                    return True, owner
            return False, None
        else:
            for existing_top_tree, owner in self.forest[path.type.value][1]:
                if existing_top_tree.path == path:
                    return True, owner
            for existing_top_tree, owner in self.forest[path.type.value][0]:
                if path.path.startswith(existing_top_tree.path.path):
                    current = existing_top_tree
                    for part in path.cut_path[len(current.path.cut_path) : -1]:
                        if part not in current.subdirs:
                            return False, None
                        current = current.subdirs[part]
                    if path.name in current.files:
                        return True, owner
            return False, None

    def _find_parent_dir(self, root: Dir, target: Path, local: bool = False) -> Dir:
        current = root
        for part in target.cut_path[len(root.path.cut_path) : -1]:
            if part not in current.subdirs:
                if local:
                    output_manager.err(
                        "Path_Does_Not_Contain_Local_Config", path=target.path
                    )
                else:
                    output_manager.err("Path_Not_Found", path=target.path)
                sys.exit(1)
            current = current.subdirs[part]
        return current

    def _remove_from_parent(
        self, parent: Dir, name: str, isdir: bool, local: bool = False
    ) -> None:
        if isdir and name in parent.subdirs:
            del parent.subdirs[name]
        elif not isdir and name in parent.files:
            del parent.files[name]
        else:
            if local:
                output_manager.err("Path_Does_Not_Contain_Local_Config", path=name)
            else:
                output_manager.err("Path_Not_Found", path=name)
            sys.exit(1)

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
        return {"name": name, "blocks": node.blocks}

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
        return File(path, data["blocks"])

    @classmethod
    def from_json(
        cls, json_str: str, if_hook: bool = False, local: bool = False
    ) -> "FileSystem":
        fs = FileSystem(if_hook=if_hook, local=local)
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
    fs = FileSystem()
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
