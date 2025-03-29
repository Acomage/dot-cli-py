"""Command implementations for the Dot CLI tool."""

import os
import shutil
import subprocess
import sys
from typing import Any, List, Optional

from dot.cli.output import output_manager
from dot.core.config import config_manager
from dot.core.conflict import conflict_manager
from dot.core.git import git_manager
from dot.core.health import check_and_guide
from dot.core.sync import sync_manager
from dot.utils.logger import logger


def cmd_init(args: Any) -> int:
    """Initialize a dotfiles repository."""
    dotfiles_path = os.path.expanduser("~/.dotfiles")

    # Check if repository already exists
    if os.path.exists(dotfiles_path):
        if os.path.isdir(dotfiles_path) and os.path.exists(
            os.path.join(dotfiles_path, ".git")
        ):
            output_manager.print_error("init_repo_exists")

            # Ask if the user wants to continue
            response = output_manager.prompt(
                "init_overwrite_prompt", choices="y/n"
            ).lower()
            if response != "y":
                output_manager.print("init_aborted")
                return 1

            # Clean existing repository
            try:
                shutil.rmtree(dotfiles_path)
            except OSError as e:
                output_manager.print_error("init_clean_error", error=str(e))
                return 1
        elif os.path.isdir(dotfiles_path):
            output_manager.print_error("init_dir_exists_not_repo")

            # Ask if the user wants to continue
            response = output_manager.prompt(
                "init_overwrite_prompt", choices="y/n"
            ).lower()
            if response != "y":
                output_manager.print("init_aborted")
                return 1

            # Clean existing directory
            try:
                shutil.rmtree(dotfiles_path)
            except OSError as e:
                output_manager.print_error("init_clean_error", error=str(e))
                return 1
        else:
            output_manager.print_error("init_path_exists_not_dir")
            return 1

    # Clone repository if URL is provided
    if args.url:
        output_manager.print("init_cloning", url=args.url)
        success, output = git_manager.clone(args.url)

        if not success:
            output_manager.print_error("init_clone_failed", error=output)
            return 1

        output_manager.print("init_clone_success")

        # Create necessary files that might be gitignored
        _create_gitignore()
        _create_local_config()
        _create_conflict_dirs()

        return 0

    # Create a new repository
    output_manager.print("init_creating")

    # Create repository directory
    try:
        os.makedirs(dotfiles_path, exist_ok=True)
    except OSError as e:
        output_manager.print_error("init_mkdir_error", error=str(e))
        return 1

    # Initialize Git repository
    success, output = git_manager.init()
    if not success:
        output_manager.print_error("init_git_error", error=output)
        return 1

    # Create standard directories
    for dir_name in ["user", "system", "conflict/user", "conflict/system"]:
        dir_path = os.path.join(dotfiles_path, dir_name)
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            output_manager.print_error("init_mkdir_error", path=dir_path, error=str(e))
            return 1

    # Create README.md
    _create_readme()

    # Create config.json
    config_manager.save_config()

    # Create local_config.json
    _create_local_config()

    # Create .gitignore
    _create_gitignore()

    # Add and commit files
    success, output = git_manager.add_and_commit("Initial commit")
    if not success:
        output_manager.print_error("init_commit_error", error=output)
        return 1

    output_manager.print("init_success")
    output_manager.print("init_next_steps")

    return 0


def _create_readme() -> None:
    """Create the README.md file."""
    readme_path = os.path.join(os.path.expanduser("~/.dotfiles"), "README.md")

    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write("# Dotfiles\n\n")
            f.write("This repository is managed by the Dot CLI tool.\n\n")
            f.write(
                "For more information, visit https://github.com/yourusername/dot-cli\n"
            )
    except OSError as e:
        logger.error(f"Error creating README.md: {e}")


def _create_gitignore() -> None:
    """Create the .gitignore file."""
    gitignore_path = os.path.join(os.path.expanduser("~/.dotfiles"), ".gitignore")

    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# Local configuration\n")
            f.write("local_config.json\n\n")
            f.write("# Conflict files\n")
            f.write("conflict/\n")
    except OSError as e:
        logger.error(f"Error creating .gitignore: {e}")


def _create_local_config() -> None:
    """Create the local_config.json file."""
    config_manager.save_local_config()


def _create_conflict_dirs() -> None:
    """Create the conflict directories."""
    dotfiles_path = os.path.expanduser("~/.dotfiles")

    for dir_name in ["conflict/user", "conflict/system"]:
        dir_path = os.path.join(dotfiles_path, dir_name)
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            logger.error(f"Error creating directory {dir_path}: {e}")


def cmd_add(args: Any) -> int:
    """Add a file or directory to the repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    path = args.path
    software = args.software

    # Expand path
    real_path = os.path.expanduser(path)

    # Check if path exists
    if not os.path.exists(real_path):
        output_manager.print_error("add_path_not_found", path=path)
        return 1

    try:
        # Add file to configuration
        config_manager.add_file(real_path, software)

        # Copy file to repository
        success = sync_manager.copy_to_repo(real_path)
        if not success:
            output_manager.print_error("add_copy_failed", path=path)
            return 1

        # Commit changes
        success, output = git_manager.add_and_commit(f"Add {path} for {software}")
        if not success:
            output_manager.print_error("add_commit_failed", error=output)
            return 1

        output_manager.print("add_success", path=path, software=software)
        return 0
    except Exception as e:
        output_manager.print_error("add_failed", error=str(e))
        return 1


def cmd_remove(args: Any) -> int:
    """Remove a file or directory from the repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    path = args.path
    software = args.software

    # Expand path
    real_path = os.path.expanduser(path)

    try:
        # Remove file from configuration
        config_manager.remove_file(real_path, software)

        # Get repository path
        repo_path = sync_manager._get_repo_path(real_path)

        # Remove file from repository
        if os.path.exists(repo_path):
            if os.path.isdir(repo_path):
                shutil.rmtree(repo_path)
            else:
                os.remove(repo_path)

            # Remove parent directories if empty
            parent_dir = os.path.dirname(repo_path)
            user_path = os.path.join(os.path.expanduser("~/.dotfiles"), "user")
            system_path = os.path.join(os.path.expanduser("~/.dotfiles"), "system")

            while parent_dir != user_path and parent_dir != system_path:
                if not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
                    parent_dir = os.path.dirname(parent_dir)
                else:
                    break

        # Commit changes
        success, output = git_manager.add_and_commit(f"Remove {path} for {software}")
        if not success:
            output_manager.print_error("remove_commit_failed", error=output)
            return 1

        output_manager.print("remove_success", path=path, software=software)
        return 0
    except Exception as e:
        output_manager.print_error("remove_failed", error=str(e))
        return 1


def cmd_edit(args: Any) -> int:
    """Edit a file in the repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    path = args.path
    real_path = os.path.expanduser(path)

    # Determine which file to edit (conflict or regular)
    if config_manager.is_conflict(real_path):
        edit_path = conflict_manager._get_conflict_file_path(real_path)

        # Initialize conflict file if it doesn't exist
        if not os.path.exists(edit_path):
            if not conflict_manager.initialize_conflict(real_path):
                output_manager.print_error("edit_conflict_init_failed", path=path)
                return 1
    else:
        edit_path = sync_manager._get_repo_path(real_path)

    # Check if file exists in repository
    if not os.path.exists(edit_path):
        output_manager.print_error("edit_file_not_found", path=path)
        return 1

    # Get editor from environment or default to vi
    editor = os.environ.get("EDITOR", "vi")

    # Open file in editor
    try:
        process = subprocess.run([editor, edit_path], check=False)

        if process.returncode != 0:
            output_manager.print_error("edit_editor_failed", path=path)
            return 1

        # If it's a conflict file, merge changes
        if config_manager.is_conflict(real_path):
            if not conflict_manager.merge_conflict_files(real_path):
                output_manager.print_error("edit_merge_failed", path=path)
                return 1

        # Commit changes
        success, output = git_manager.add_and_commit(f"Edit {path}")
        if not success:
            output_manager.print_error("edit_commit_failed", error=output)
            return 1

        output_manager.print("edit_success", path=path)
        return 0
    except Exception as e:
        output_manager.print_error("edit_failed", error=str(e))
        return 1


def cmd_apply(args: Any) -> int:
    """Apply changes from the repository to the system."""
    # Check repository health
    if not check_and_guide():
        return 1

    if args.all:
        # Apply all files from local config
        # TODO: Implement iterating through all files in local_config
        output_manager.print("apply_all_not_implemented")
        return 1
    elif args.path:
        # Apply specific file or directory
        path = args.path
        real_path = os.path.expanduser(path)

        # Copy file from repository to system
        success = sync_manager.copy_from_repo(real_path)
        if not success:
            output_manager.print_error("apply_failed", path=path)
            return 1

        output_manager.print("apply_success", path=path)
        return 0
    else:
        output_manager.print_error("apply_no_path")
        return 1


def cmd_sync(args: Any) -> int:
    """Sync changes from the system to the repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    if args.all:
        # Sync all files from local config
        # TODO: Implement iterating through all files in local_config
        output_manager.print("sync_all_not_implemented")
        return 1
    elif args.path:
        # Sync specific file or directory
        path = args.path
        real_path = os.path.expanduser(path)

        # Check if file exists
        if not os.path.exists(real_path):
            output_manager.print_error("sync_file_not_found", path=path)
            return 1

        # Copy file from system to repository
        success = sync_manager.copy_to_repo(real_path)
        if not success:
            output_manager.print_error("sync_failed", path=path)
            return 1

        # Commit changes
        success, output = git_manager.add_and_commit(f"Sync {path}")
        if not success:
            output_manager.print_error("sync_commit_failed", error=output)
            return 1

        output_manager.print("sync_success", path=path)
        return 0
    else:
        output_manager.print_error("sync_no_path")
        return 1


def cmd_diff(args: Any) -> int:
    """Show differences between system and repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    if args.path:
        # Diff specific file or directory
        path = args.path
        real_path = os.path.expanduser(path)

        # Check if file exists in system
        if not os.path.exists(real_path):
            output_manager.print_error("diff_file_not_found", path=path)
            return 1

        # Get diff
        success, diff = sync_manager.diff_files(real_path)
        if not success:
            output_manager.print_error("diff_failed", error=diff)
            return 1

        if diff:
            print(diff)
        else:
            output_manager.print("diff_no_changes", path=path)

        return 0
    else:
        # Diff all files from local config
        output_manager.print("diff_all_not_implemented")
        return 1


def cmd_push(args: Any) -> int:
    """Push changes to the remote repository."""
    # Check repository health and remote configuration
    if not check_and_guide(check_remote=True):
        return 1

    # Push changes
    success, output = git_manager.push()
    if not success:
        output_manager.print_error("push_failed", error=output)
        return 1

    output_manager.print("push_success")
    return 0


def cmd_pull(args: Any) -> int:
    """Pull changes from the remote repository."""
    # Check repository health and remote configuration
    if not check_and_guide(check_remote=True):
        return 1

    # Pull changes
    success, output = git_manager.pull()
    if not success:
        output_manager.print_error("pull_failed", error=output)
        return 1

    # Check for new conflict files
    # TODO: Implement checking for new conflict files
    # This would involve comparing the conflict_files in config before and after the pull

    output_manager.print("pull_success")
    return 0


def cmd_update(args: Any) -> int:
    """Update the system with changes from the remote repository."""
    # This is essentially a pull followed by an apply

    # Pull changes
    pull_result = cmd_pull(args)
    if pull_result != 0:
        return pull_result

    # Apply all changes
    args.all = True
    args.path = None
    apply_result = cmd_apply(args)
    if apply_result != 0:
        return apply_result

    output_manager.print("update_success")
    return 0


def cmd_remote(args: Any) -> int:
    """Manage the remote repository."""
    # Check repository health
    if not check_and_guide():
        return 1

    if args.clean:
        # Remove remote
        success, output = git_manager.remove_remote()
        if not success:
            output_manager.print_error("remote_remove_failed", error=output)
            return 1

        output_manager.print("remote_remove_success")
        return 0
    elif args.url:
        # Set remote URL
        success, output = git_manager.set_remote(args.url)
        if not success:
            output_manager.print_error("remote_set_failed", error=output)
            return 1

        output_manager.print("remote_set_success", url=args.url)
        return 0
    else:
        output_manager.print_error("remote_no_url")
        return 1


def cmd_manage(args: Any) -> int:
    """Manage software configurations."""
    # Check repository health
    if not check_and_guide():
        return 1

    software = args.software

    try:
        # Add software configuration to local config
        config_manager.manage_software(software)

        output_manager.print("manage_success", software=software)
        return 0
    except Exception as e:
        output_manager.print_error("manage_failed", error=str(e))
        return 1


def cmd_conflict(args: Any) -> int:
    """Manage conflicts between machines."""
    # Check repository health
    if not check_and_guide():
        return 1

    path = args.path
    real_path = os.path.expanduser(path)

    # Check if path exists in repository
    repo_path = sync_manager._get_repo_path(real_path)
    if not os.path.exists(repo_path):
        output_manager.print_error("conflict_file_not_found", path=path)
        return 1

    if args.clean:
        # Clean conflict markers
        if not config_manager.is_conflict(real_path):
            output_manager.print_error("conflict_not_marked", path=path)
            return 1

        # Clean conflict
        if not conflict_manager.clean_conflict(real_path):
            output_manager.print_error("conflict_clean_failed", path=path)
            return 1

        # Unmark as conflict
        config_manager.unmark_as_conflict(real_path)

        # Commit changes
        success, output = git_manager.add_and_commit(
            f"Remove conflict markers from {path}"
        )
        if not success:
            output_manager.print_error("conflict_commit_failed", error=output)
            return 1

        output_manager.print("conflict_clean_success", path=path)
        return 0
    else:
        # Mark as conflict
        if config_manager.is_conflict(real_path):
            output_manager.print_error("conflict_already_marked", path=path)
            return 1

        # Initialize conflict
        if not conflict_manager.initialize_conflict(real_path):
            output_manager.print_error("conflict_init_failed", path=path)
            return 1

        # Mark as conflict
        config_manager.mark_as_conflict(real_path)

        # Open conflict file in editor for marking
        conflict_path = conflict_manager._get_conflict_file_path(real_path)
        editor = os.environ.get("EDITOR", "vi")

        try:
            process = subprocess.run([editor, conflict_path], check=False)

            if process.returncode != 0:
                output_manager.print_error("conflict_editor_failed", path=path)
                return 1

            # Validate conflict markers
            with open(conflict_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not conflict_manager.validate_conflict_markers(content):
                output_manager.print_error("conflict_invalid_markers", path=path)
                # Revert changes
                config_manager.unmark_as_conflict(real_path)
                os.remove(conflict_path)
                return 1

            # Copy conflict file to repository
            shutil.copy2(conflict_path, repo_path)

            # Commit changes
            success, output = git_manager.add_and_commit(
                f"Add conflict markers to {path}"
            )
            if not success:
                output_manager.print_error("conflict_commit_failed", error=output)
                return 1

            output_manager.print("conflict_mark_success", path=path)
            return 0
        except Exception as e:
            output_manager.print_error("conflict_failed", error=str(e))
            # Revert changes
            config_manager.unmark_as_conflict(real_path)
            if os.path.exists(conflict_path):
                os.remove(conflict_path)
            return 1


def cmd_clean(args: Any) -> int:
    """Clean up the repository."""
    dotfiles_path = os.path.expanduser("~/.dotfiles")

    # Check if repository exists
    if not os.path.exists(dotfiles_path) or not os.path.isdir(dotfiles_path):
        output_manager.print_error("clean_no_repo")
        return 1

    # Prompt for confirmation
    output_manager.print("clean_warning")
    response = output_manager.prompt("clean_confirm", choices="y/n").lower()

    if response != "y":
        output_manager.print("clean_aborted")
        return 1

    try:
        # Remove repository
        shutil.rmtree(dotfiles_path)

        output_manager.print("clean_success")
        return 0
    except Exception as e:
        output_manager.print_error("clean_failed", error=str(e))
        return 1
