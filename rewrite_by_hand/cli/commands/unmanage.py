from typing import Any
import sys
from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.cli.output import output_manager


def cmd_unmanage(args: Any):
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
    config_manager.unmanage(path_str=path)
    config_manager.save()
    output_manager.out("Unmanage_Success", path=path)
    sys.exit(0)
