from fs_utils import Path, FileType
import shutil
import os


def hook(command: str):
    print(command)


REPOUSERPATH = Path("~/.dotfiles/user")
REPOSYSTEMPATH = Path("~/.dotfiles/system")


def ensure_dir_exists(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


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


if __name__ == "__main__":
    hk = Hooker()
    hk.add_file(Path("~/.zshrc"))
    hk.add_file(Path("/etc/keyd/default.conf"))
