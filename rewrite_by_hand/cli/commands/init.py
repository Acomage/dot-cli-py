from typing import Any
import shutil
import os
import sys

from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.data.variables import (
    REPOPATH,
    README_FIRST_LINE,
    README_ORIGIN,
    CONFIG_ORIGIN,
    IGNORE_ORIGIN,
)
from rewrite_by_hand.utils.fs_utils import ensure_dir_exists
from rewrite_by_hand.core.git import git_manager
from rewrite_by_hand.cli.output import output_manager, validate_yes_no


def cmd_init(args: Any):
    status = checker.check()
    match status:
        case HealthStatus.Repo_Dir_Path_Not_Exist:
            ensure_dir_exists(REPOPATH)
        case HealthStatus.Repo_Dir_Path_Exist_But_Is_A_File:
            output_manager.err(
                "Init_Repo_Dir_Path_Exist_But_Is_A_File", REPOPATH=REPOPATH
            )
            sys.exit(1)
        case HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo:
            output_manager.err(
                "Init_Repo_Dir_Exist_But_Not_Our_Repo",
                REPOPATH=REPOPATH,
                README_FIRST_LINE=README_FIRST_LINE,
            )
            sys.exit(1)
        case _:
            sure = output_manager.prompt(
                "Init_Reinit", default="y", validator=validate_yes_no
            )
            if sure.lower() != "y":
                sys.exit(0)
            shutil.rmtree(REPOPATH)
            ensure_dir_exists(REPOPATH)
    if args.url:
        output_manager.out("Init_Cloning", Url=args.url)
        success, output = git_manager.clone(args.url)

        if not success:
            output_manager.err("Init_Clone_Failed", output=output)
            output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
            sys.exit(1)

        output_manager.out("Init_Cloning_Success", Url=args.url)

        # Create necessary files that might be gitignored
        _create_gitignore()
        _create_local_config()

        sys.exit(0)

    # Initialize Git repository
    success, output = git_manager.init()
    if not success:
        output_manager.err("Init_Git_Init_Failed", output=output)
        output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
        sys.exit(1)

    # Create standard directories
    for dir_name in ["user", "system"]:
        dir_path = os.path.join(REPOPATH, dir_name)
        if not ensure_dir_exists(dir_path):
            output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
            sys.exit(1)

    # Create README.md
    _create_readme()

    # Create config.json
    _create_config()

    # Create local_config.json
    _create_local_config()

    # Create .gitignore
    _create_gitignore()

    # Add and commit files
    success, output = git_manager.add_and_commit("Initial commit")
    if not success:
        output_manager.err("Init_Git_Init_Commit_Failed", output=output)
        sys.exit(1)

    output_manager.out("Init_Success")
    output_manager.out("Init_Next_Step")

    sys.exit(0)


def _create_readme() -> None:
    """Create the README.md file."""
    readme_path = os.path.join(REPOPATH, "README.md")

    try:
        shutil.copy2(README_ORIGIN, readme_path)
    except OSError as e:
        output_manager.err("Init_Create_Readme_Failed", output=e)
        output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
        sys.exit(1)


def _create_gitignore() -> None:
    """Create the .gitignore file."""
    gitignore_path = os.path.join(REPOPATH, ".gitignore")

    try:
        shutil.copy2(IGNORE_ORIGIN, gitignore_path)
    except OSError as e:
        output_manager.err("Init_Create_Gitignore_Failed", output=e)
        output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
        sys.exit(1)


def _create_config() -> None:
    """Create the config.json file."""
    readme_path = os.path.join(REPOPATH, "config.json")

    try:
        shutil.copy2(CONFIG_ORIGIN, readme_path)
    except OSError as e:
        output_manager.err("Init_Create_Config_Failed", output=e)
        output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
        sys.exit(1)


def _create_local_config() -> None:
    """Create the local_config.json file."""
    readme_path = os.path.join(REPOPATH, "local_config.json")

    try:
        shutil.copy2(CONFIG_ORIGIN, readme_path)
    except OSError as e:
        output_manager.err("Init_Create_Local_Config_Failed", output=e)
        output_manager.err("Init_Tell_User_To_Clean", REPOPATH=REPOPATH)
        sys.exit(1)
