from typing import Any
import sys
from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.cli.output import output_manager
from rewrite_by_hand.core.git import git_manager


def cmd_remote(args: Any):
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

    if args.clean:
        # Remove remote
        success, output = git_manager.remove_remote()
        if not success:
            output_manager.err("Remote_Remove_Failed", error=output)
            sys.exit(1)

        output_manager.out("Remote_Remove_Success")
        sys.exit(0)
    else:
        # Set remote URL
        success, output = git_manager.set_remote(args.url)
        if not success:
            output_manager.err("Remote_Set_Failed", error=output)
            sys.exit(1)

        output_manager.out("Remote_Set_Success", url=args.url)
        sys.exit(0)
