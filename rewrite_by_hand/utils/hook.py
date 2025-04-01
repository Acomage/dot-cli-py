from typing import List
import shutil
import os

from rewrite_by_hand.utils.fs_utils import ensure_dir_exists
from rewrite_by_hand.utils.fs_type import Path, FileType, Dir
from rewrite_by_hand.data.variables import REPO_USER_PATH, REPO_SYSTEM_PATH


def hook(command: str):
    print(command)


REPOUSERPATH = Path(REPO_USER_PATH)
REPOSYSTEMPATH = Path(REPO_SYSTEM_PATH)


class Hooker:
    def __init__(self):
        pass

    def add_file(self, path: Path):
        source_path = path.path
        repo_dir = (
            REPOUSERPATH.path if path.type == FileType.USER else REPOSYSTEMPATH.path
        )
        target_path = os.path.join(repo_dir, path.relative_path)
        ensure_dir_exists(os.path.dirname(target_path))
        if os.path.exists(target_path):
            return
        shutil.copy2(source_path, target_path)

    def add_dir(self, path: Path, merge_list: List[Dir]):
        source_path = path.path
        repo_dir = (
            REPOUSERPATH.path if path.type == FileType.USER else REPOSYSTEMPATH.path
        )
        for merge in merge_list:
            if path == merge.path:
                merge_list.remove(merge)
                return
        target_path = os.path.join(repo_dir, path.relative_path)
        ensure_dir_exists(target_path)
        for name in os.listdir(source_path):
            full_path = os.path.join(source_path, name)
            if os.path.isdir(full_path):
                dir_path = Path(full_path)
                self.add_dir(dir_path, merge_list)
            else:
                file_path = Path(full_path)
                self.add_file(file_path)

    def remove(self, path: Path) -> bool:
        repo_dir = (
            REPOUSERPATH.path if path.type == FileType.USER else REPOSYSTEMPATH.path
        )
        target_path = os.path.join(repo_dir, path.relative_path)
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
                return True
            os.remove(target_path)
            return True
        return False


if __name__ == "__main__":
    hk = Hooker()
    hk.add_file(Path("~/.zshrc"))
    hk.add_file(Path("/etc/keyd/default.conf"))
