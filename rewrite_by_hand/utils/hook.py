def hook(command: str):
    print(command)


class Hooker:
    def __init__(self):
        pass

    def add_without_merge(self, path: str):
        hook(f"git add {path}")

