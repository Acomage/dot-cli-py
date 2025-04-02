import shutil
import sys

from rewrite_by_hand.data.variables import REPOPATH
from rewrite_by_hand.core.health import checker, HealthStatus
from rewrite_by_hand.cli.output import output_manager, validate_yes_no


def cmd_clean(_):
    status = checker.check()
    if status == HealthStatus.Repo_Dir_Path_Not_Exist:
        output_manager.err("Clean_Repo_Dir_Path_Not_Exist", REPOPATH=REPOPATH)
        sys.exit(1)
    no_acceptable_status = [
        HealthStatus.Repo_Dir_Path_Exist_But_Is_A_File,
        HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo,
    ]
    if status in no_acceptable_status:
        output_manager.err("Clean_Repo_Dir_Exist_But_Not_Our_Repo", REPOPATH=REPOPATH)
        sys.exit(1)
    else:
        sure = output_manager.prompt(
            "Clean_Confirm", REPOPATH=REPOPATH, default="n", validator=validate_yes_no
        )
        if sure.lower() != "y":
            output_manager.err("Clean_Abort")
            sys.exit(1)
        try:
            shutil.rmtree(REPOPATH)
        except Exception as e:
            output_manager.err("Retree_Failed", path=REPOPATH, error=str(e))
            sys.exit(1)
        output_manager.out("Clean_Success", REPOPATH=REPOPATH)
        sys.exit(0)
