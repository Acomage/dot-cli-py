from typing import Any
from rewrite_by_hand.core.health import checker, HealthStatus
import shutil
import os

from rewrite_by_hand.data.variables import REPOPATH, README_FIRST_LINE
from rewrite_by_hand.utils.hook import ensure_dir_exists
from rewrite_by_hand.core.git import git_manager


def cmd_init(args: Any):
    status = checker.check()
    match status:
        case HealthStatus.Repo_Dir_Path_Not_Exist:
            ensure_dir_exists(REPOPATH)
        case HealthStatus.Repo_Dir_Path_Exist_But_Is_A_File:
            raise Exception(
                f"The path {REPOPATH} is a file, not a directory. You should check if this file you need. Or you can read the README at https://github.com/Acomage/dot-cli-py to learn how to set another path as repo path."
            )
        case HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo:
            raise Exception(
                f"We find that there is not a correct REAMDE.md file in {REPOPATH}. It may means that {REPOPATH} is created by other tools. If you are sure that {REPOPATH} is a correct repo, please added the {README_FIRST_LINE} to the first line of the README.md file. Or you can read the https://github.com/Acomage/dot-cli-py to learn how to set another path as repo path."
            )
        case _:
            input("The repo is already initialized. Do you want to reinit it? (y/n)")
            if input().lower() != "y":
                exit(0)
            shutil.rmtree(REPOPATH)
            ensure_dir_exists(REPOPATH)
    if args.url:
        print(f"init_cloning {args.url}")
        success, output = git_manager.clone(args.url)

        if not success:
            print(f"init_clone_failed \n error:{output}")
            return 1

        print("init_clone_success")

        # Create necessary files that might be gitignored
        _create_gitignore()
        _create_local_config()
        _create_conflict_dirs()

        return 0

    # Create a new repository
    print("init_creating")

    # Initialize Git repository
    success, output = git_manager.init()
    if not success:
        print(f"init_git_error\nerror: {output}")
        return 1

    # Create standard directories
    for dir_name in ["user", "system", "conflict/user", "conflict/system"]:
        dir_path = os.path.join(REPOPATH, dir_name)
        if not ensure_dir_exists(dir_path):
            return 1

    # Create README.md
    _create_readme()

    # Create config.json
    # TODO: Implement config.json creation

    # Create local_config.json
    _create_local_config()

    # Create .gitignore
    _create_gitignore()

    # Add and commit files
    success, output = git_manager.add_and_commit("Initial commit")
    if not success:
        print(f"init_commit_error\nerror: {output}")
        return 1

    print("init_success")
    print("init_next_steps")

    return 0


def _create_readme() -> None:
    """Create the README.md file."""
    readme_path = os.path.join(REPOPATH, "README.md")

    try:
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(README_FIRST_LINE)
            f.write("# Dotfiles\n\n")
            f.write("This repository is managed by the Dot CLI tool.\n\n")
            f.write(
                "For more information, visit https://github.com/Acomage/dot-cli-py\n"
            )
    except OSError as e:
        print(f"Error creating README.md: {e}")


def _create_gitignore() -> None:
    """Create the .gitignore file."""
    gitignore_path = os.path.join(REPOPATH, ".gitignore")

    try:
        with open(gitignore_path, "w", encoding="utf-8") as f:
            f.write("# Local configuration\n")
            f.write("local_config.json\n\n")
            f.write("# Conflict files\n")
            f.write("conflict/\n")
    except OSError as e:
        print(f"Error creating .gitignore: {e}")


def _create_local_config() -> None:
    """Create the local_config.json file."""
    # TODO: Implement local_config.json creation


def _create_conflict_dirs() -> None:
    """Create the conflict directories."""
    dotfiles_path = os.path.expanduser("~/.dotfiles")

    for dir_name in ["conflict/user", "conflict/system"]:
        dir_path = os.path.join(dotfiles_path, dir_name)
        try:
            os.makedirs(dir_path, exist_ok=True)
        except OSError as e:
            print(f"Error creating directory {dir_path}: {e}")
