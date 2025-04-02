import os
from rewrite_by_hand.cli.output import output_manager


def ensure_dir_exists(path: str) -> bool:
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        output_manager.err("Ensure_Dir_Exists_Failed", path=path, error=OSError)
        # print(f"Error creating directory: {path} with error: {OSError}")
        return False
