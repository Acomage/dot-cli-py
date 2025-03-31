from typing import List, Dict
import os
import json
from enum import Enum

USERPATH = os.path.expanduser("~")


class FileType(Enum):
    USER = 0
    SYSTEM = 1


class Path:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Path {path} does not exist.")
        self.is_dir = os.path.isdir(self.path)
        self.cut_path = self.path.split(os.sep)
        if self.cut_path[-1] == "":
            self.cut_path = self.cut_path[:-1]
        self.name = self.cut_path[-1]

    def __eq__(self, other):
        if isinstance(other, Path):
            return self.path == other.path
        return False


class Node:
    def __init__(self, path: Path):
        self.path = path
        self.name = path.name

    def is_proper_subtree_of(self, other: Path) -> bool:
        length = len(other.cut_path)
        if len(self.path.cut_path) <= length:
            return False
        if self.path.cut_path[:length] != other.cut_path:
            return False
        return True


class File(Node):
    def __init__(self, path: Path):
        super().__init__(path)


class Dir(Node):
    def __init__(self, path: Path):
        super().__init__(path)
        self.contents: Dict[str, Node] = {}
        self.fill_contents()

    def fill_contents(self):
        for name in os.listdir(self.path.path):
            path = Path(os.path.join(self.path.path, name))
            if path.is_dir:
                self.contents[name] = Dir(path)
            else:
                self.contents[name] = File(path)


def merge_two_trees(tree1: Node, tree2: Dir):
    """Merge two trees, where tree1 is a proper subtree of tree2.This function have side effects that will change tree2."""
    assert tree1.is_proper_subtree_of(tree2.path)
    length = len(tree2.path.cut_path)
    parent = tree2
    for name in tree1.path.cut_path[length:-1]:
        parent = parent.contents[name]
        assert isinstance(parent, Dir)
    parent.contents[tree1.name] = tree1


class FileSystem:
    def __init__(self):
        self.Forest: List[Node] = []

    def add(self, path_str: str):
        path = Path(path_str)
        if path.is_dir:
            tree = Dir(path)
        else:
            tree = File(path)
        for exist_tree in self.Forest:
            if exist_tree.path == path:
                raise ValueError(f"Path {path.path} already exists in the file system.")
            if tree.is_proper_subtree_of(exist_tree.path):
                assert isinstance(exist_tree, Dir)
                merge_two_trees(tree, exist_tree)
                return
            if exist_tree.is_proper_subtree_of(tree.path):
                assert isinstance(tree, Dir)
                merge_two_trees(exist_tree, tree)
                self.Forest.remove(exist_tree)
        self.Forest.append(tree)

    def remove(self, path_str: str):
        path = Path(path_str)
        for exist_tree in self.Forest:
            if path.path.startswith(exist_tree.path.path):
                if path == exist_tree.path:
                    self.Forest.remove(exist_tree)
                    return
                parent = exist_tree
                assert isinstance(parent, Dir)
                length = len(exist_tree.path.cut_path)
                for name in path.cut_path[length:-1]:
                    if name not in parent.contents:
                        raise ValueError(f"Path {path} not found in the file system.")
                    parent = parent.contents[name]
                    assert isinstance(parent, Dir)
                if path.name in parent.contents:
                    del parent.contents[path.name]
                    return
        raise ValueError(f"Path {path.path} not found in the file system.")

    @staticmethod
    def tree_to_dict(tree: Node, full: bool = False) -> Dict:
        if full:
            name = tree.path.path
        else:
            name = tree.path.name
        if isinstance(tree, Dir):
            return {
                "name": name,
                "contents": [
                    FileSystem.tree_to_dict(child) for child in tree.contents.values()
                ],
            }
        else:
            return {"name": name}

    def to_json(self) -> str:
        forest_dict = [FileSystem.tree_to_dict(tree, True) for tree in self.Forest]
        return json.dumps(forest_dict, indent=2)

    @staticmethod
    def from_json(json_str: str) -> "FileSystem":
        fs = FileSystem()
        forest_dict = json.loads(json_str)
        fs.Forest = []
        for tree_dict in forest_dict:
            fs.Forest.append(FileSystem._from_dict(tree_dict))
        return fs

    @staticmethod
    def _from_dict(tree_dict: Dict, prepath: str = "") -> Node:
        path_str = os.path.join(prepath, tree_dict["name"])
        path = Path(path_str)
        if "contents" in tree_dict:
            node = Dir(path)
            for child_dict in tree_dict["contents"]:
                child_node = FileSystem._from_dict(child_dict, path_str)
                node.contents[child_node.name] = child_node
        else:
            node = File(path)
        return node

    def __repr__(self):
        return self.to_json()

    def __str__(self):
        return self.to_json()


if __name__ == "__main__":
    print(USERPATH)
