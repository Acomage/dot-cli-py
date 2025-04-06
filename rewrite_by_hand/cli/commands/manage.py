from typing import Any
import sys
from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.cli.output import output_manager


def cmd_manage(args: Any):
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

    if args.all:
        config_manager = ConfigManager.load(if_hook=True)
        config_manager.local_config = config_manager.config
        config_manager.save()
        output_manager.out("Manage_All_Success")
        sys.exit(0)
    if args.path:
        config_manager = ConfigManager.load(if_hook=True)
        path = args.path
        config_manager.manage(path_str=path)
        config_manager.save()
        output_manager.out("Manage_Success", path=path)
        sys.exit(0)
    else:
        config_manager = ConfigManager.load(if_hook=True)
        software = args.software
        config_manager.manage_software(software)
        config_manager.save()
        output_manager.out("Manage_software_Success", software=software)
        sys.exit(0)
