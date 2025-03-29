"""File system utilities for the Dot CLI tool."""

import os
import shutil
from typing import Optional, Tuple, List


def ensure_dir_exists(path: str) -> bool:
    """
    Ensure that a directory exists.

    Args:
        path: The directory path

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False


def copy_file(src: str, dst: str, follow_symlinks: bool = True) -> bool:
    """
    Copy a file from src to dst.

    Args:
        src: Source path
        dst: Destination path
        follow_symlinks: Whether to follow symlinks

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure destination directory exists
        dst_dir = os.path.dirname(dst)
        ensure_dir_exists(dst_dir)

        # Copy file
        shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
        return True
    except (OSError, shutil.Error):
        return False


def copy_dir(src: str, dst: str, follow_symlinks: bool = True) -> bool:
    """
    Copy a directory from src to dst.

    Args:
        src: Source path
        dst: Destination path
        follow_symlinks: Whether to follow symlinks

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Remove destination if it exists
        if os.path.exists(dst):
            if os.path.isdir(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)

        # Copy directory
        shutil.copytree(src, dst, symlinks=not follow_symlinks)
        return True
    except (OSError, shutil.Error):
        return False


def remove_empty_dirs(path: str, base_path: Optional[str] = None) -> None:
    """
    Recursively remove empty directories from path up to base_path.

    Args:
        path: Path to start from
        base_path: Base path to stop at (will not be removed)
    """
    if base_path is None:
        return

    current = path
    while current != base_path:
        if os.path.isdir(current) and not os.listdir(current):
            try:
                os.rmdir(current)
                current = os.path.dirname(current)
            except OSError:
                # Directory not empty or permission error
                break
        else:
            break


def get_file_permission(path: str) -> int:
    """
    Get the permissions of a file.

    Args:
        path: File path

    Returns:
        int: File permissions (e.g., 0o644)
    """
    return os.stat(path).st_mode & 0o777


def set_file_permission(path: str, mode: int) -> bool:
    """
    Set the permissions of a file.

    Args:
        path: File path
        mode: File permissions (e.g., 0o644)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.chmod(path, mode)
        return True
    except OSError:
        return False
