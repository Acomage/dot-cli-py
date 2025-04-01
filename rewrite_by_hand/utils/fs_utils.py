from typing import List, Dict, TypeAlias
import os
from enum import Enum

from rewrite_by_hand.data.variables import USERPATH, SYSTEMPATH, REPOPATH


class FileType(Enum):
    USER = 0
    SYSTEM = 1


Owner: TypeAlias = str


class Path:
    def __init__(self, path: str):
        self.path = os.path.expanduser(path)
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Path {path} does not exist.")
        if REPOPATH.startswith(self.path):
            raise ValueError(
                f"You cannot use a path containing the {REPOPATH} or there is a recursive error."
            )
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
