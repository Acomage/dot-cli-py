import os


def ensure_dir_exists(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        print(f"Error creating directory: {path} with error: {OSError}")
        return False
