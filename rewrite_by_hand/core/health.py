from enum import Enum
import os
from rewrite_by_hand.data.variables import REPOPATH, README_FIRST_LINE


class HealthStatus(Enum):
    Repo_Dir_Path_Not_Exist = 0
    Repo_Dir_Path_Exist_But_Is_A_File = 1
    Repo_Is_Empty = 2
    Repo_Dir_Exist_But_Not_Our_Repo = 3
    Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy = 4
    All_Right = 5


class Checker:
    def __init__(self):
        pass

    def check(self) -> HealthStatus:
        if not os.path.exists(REPOPATH):
            return HealthStatus.Repo_Dir_Path_Not_Exist
        if not os.path.isdir(REPOPATH):
            return HealthStatus.Repo_Dir_Path_Exist_But_Is_A_File
        if not os.listdir(REPOPATH):
            return HealthStatus.Repo_Is_Empty
        # Check if the first line of the README file is the same as the README_FIRST_LINE
        if "README.md" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo
        with open(os.path.join(REPOPATH, "README.md"), "r") as f:
            first_line = f.readline().strip()
            if first_line != README_FIRST_LINE:
                return HealthStatus.Repo_Dir_Exist_But_Not_Our_Repo
        # Check if the repo is healthy
        # If the repo is healthy, it should contain a .git directory, a system directory, a user directory, a .gitignore file, a config.json file, a local_config.json file, and a README.md file
        if ".git" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if ".gitignore" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if "config.json" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if "local_config.json" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if "README.md" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if "system" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        if "user" not in os.listdir(REPOPATH):
            return HealthStatus.Repo_Dir_Exist_And_Our_Repo_But_Not_Healthy
        # TODO:cheak if the repo structure is consist with config.json
        return HealthStatus.All_Right


checker = Checker()
