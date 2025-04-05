from typing import Any
import sys
from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.cli.output import output_manager
from rewrite_by_hand.core.git import git_manager


def cmd_add(args: Any):
    status = checker.check()
    should_init = [
        HealthStatus.Repo_Dir_Path_Not_Exist,
        HealthStatus.Repo_Dir_Path_Exist_But_Is_A_File,
        HealthStatus.Repo_Is_Empty,
        HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo,
    ]
    if status in should_init:
        output_manager.err("Add_Should_Init")
        sys.exit(1)
    if status == HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy:
        output_manager.err("Repo_Not_Healthy")
        sys.exit(1)

    from rewrite_by_hand.core.config import ConfigManager

    config_manager = ConfigManager.load(if_hook=True)
    path = args.path
    software = args.software
    if args.pure:
        config_manager.pure_add(path_str=path, owner=software)
    else:
        config_manager.add(path_str=path, owner=software)
    success, output = git_manager.add_and_commit(f"Added {path} for {software}")
    if not success:
        output_manager.err("Add_commit_failed", error=output)
        sys.exit(1)
    output_manager.out("Add_Success", path=path, owner=software)
    sys.exit(0)
