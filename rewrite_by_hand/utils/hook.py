from fs_utils import Path


def hook(command: str):
    print(command)


REPOUSERPATH = Path("~/.dotfiles/user")
REPOSYSTEMPATH = Path("~/.dotfiles/system")


class Hooker:
    def __init__(self):
        pass

    def add_file(self, path: Path):
        pass


if __name__ == "__main__":
    hooker = Hooker()
