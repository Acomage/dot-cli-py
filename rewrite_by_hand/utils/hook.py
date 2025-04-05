from typing import List
import shutil
import os
import sys

from rewrite_by_hand.utils.fs_utils import ensure_dir_exists
from rewrite_by_hand.utils.fs_type import Path, FileType, Dir
from rewrite_by_hand.data.variables import REPO_USER_PATH, REPO_SYSTEM_PATH
from rewrite_by_hand.cli.output import output_manager


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
        if not ensure_dir_exists(os.path.dirname(target_path)):
            sys.exit(1)
        if os.path.exists(target_path):
            return
        try:
            shutil.copy2(source_path, target_path)
        except PermissionError:
            output_manager.err("Hooker_Add_File_Failed", path=source_path)
            sys.exit(1)

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
        if not ensure_dir_exists(target_path):
            sys.exit(1)
        for name in os.listdir(source_path):
            full_path = os.path.join(source_path, name)
            if os.path.isdir(full_path):
                dir_path = Path(full_path)
                self.add_dir(dir_path, merge_list)
            else:
                file_path = Path(full_path)
                self.add_file(file_path)

    def remove(self, path: Path):
        repo_dir = (
            REPOUSERPATH.path if path.type == FileType.USER else REPOSYSTEMPATH.path
        )
        target_path = os.path.join(repo_dir, path.relative_path)
        if os.path.exists(target_path):
            if os.path.isdir(target_path):
                try:
                    shutil.rmtree(target_path)
                    return
                except OSError as e:
                    output_manager.err(
                        "Hooker_Remove_Failed", path=target_path, error=e
                    )
                    sys.exit(1)
            try:
                os.remove(target_path)
                return
            except OSError as e:
                output_manager.err("Hooker_Remove_Failed", path=target_path, error=e)
                sys.exit(1)
        output_manager.err("Hooker_Remove_Failed_File_Not_Found", path=target_path)
        sys.exit(1)

    def remove_top(self, path: Path):
        repo_dir = (
            REPOUSERPATH.path if path.type == FileType.USER else REPOSYSTEMPATH.path
        )
        target_path = os.path.join(repo_dir, path.relative_path)
        if os.path.exists(target_path):
            biggest_path = Path(target_path)
            while self.remove_parent_or_not(biggest_path):
                biggest_path = Path(os.path.dirname(biggest_path.path))
            if os.path.isdir(biggest_path.path):
                try:
                    shutil.rmtree(biggest_path.path)
                    return
                except OSError as e:
                    output_manager.err(
                        "Hooker_Remove_Failed", path=biggest_path.path, error=e
                    )
                    sys.exit(1)
            try:
                os.remove(biggest_path.path)
                return
            except OSError as e:
                output_manager.err(
                    "Hooker_Remove_Failed", path=biggest_path.path, error=e
                )
                sys.exit(1)
        output_manager.err("Hooker_Remove_Failed_File_Not_Found", path=target_path)
        sys.exit(1)

    def remove_parent_or_not(self, path: Path) -> bool:
        if len(path.cut_path) <= 3:
            return False
        parent_path = os.path.dirname(path.path)
        if len(os.listdir(parent_path)) == 1:
            return True
        return False


if __name__ == "__main__":
    hk = Hooker()
    hk.add_file(Path("~/.zshrc"))
    hk.add_file(Path("/etc/keyd/default.conf"))
