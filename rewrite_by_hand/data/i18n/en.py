from enum import Enum


class OutputText(Enum):
    HELLO = "Hello, {}!"
    FILE_READ = "File {} read successfully."
    # above line is for test, following lines are for real use
    Init_Cloning = "Cloning repository from {Url}..."
    Init_Cloning_Success = "Cloning repository from {Url} success."
    Init_Success = "Repo initialization successfully. Have a nice day!"
    Init_Next_Step = "Next step: You can\n1. run 'dot add <path> <software>' to manage your dotfiles\n2. run 'dot remote <url>' to set a remote repository."


class ErrorText(Enum):
    FILE_NOT_FOUND = "Error: File {} not found!"
    INVALID_INPUT = "Error: Invalid input '{}'."
    # above line is for test, following lines are for real use
    # fs_utils
    Ensure_Dir_Exists_Failed = "Error creating directory: {path} with error: {error}"
    # init
    Init_Repo_Dir_Path_Exist_But_Is_A_File = "The path {REPOPATH} is a file, not a directory. If you need that file, you can set another path as repo path."
    Init_Repo_Dir_Exist_But_Not_Our_Repo = "We find that there is not a correct REAMDE.md file in {REPOPATH}. It may means that {REPOPATH} is created by other tools. If you need that directory, you can set another path as repo path."
    Init_Clone_Failed = "Failed to clone the repository. Error: {output}"
    Init_Git_Init_Failed = "Failed to initialize the Git repository. Error: {output}"
    Init_Git_Init_Commit_Failed = "Failed to commit the initial files. Error: {output}"
    Init_Create_Readme_Failed = "Failed to create README.md. Error: {output}"
    Init_Create_Config_Failed = "Failed to create config.json. Error: {output}"
    Init_Create_Local_Config_Failed = (
        "Failed to create local_config.json. Error: {output}"
    )
    Init_Create_Gitignore_Failed = "Failed to create .gitignore. Error: {output}"
    Init_Create_Conflict_Dirs_Failed = (
        "Failed to create conflict directories when creating {dir}."
    )
    Init_Tell_User_To_Clean = "Please clean the directory {REPOPATH} by running 'rm -r {REPOPATH}' or by running 'dot clean' and try again."


class PromptText(Enum):
    DEFAULT = "Default: "
    INPUT_NAME = "Enter your name: "
    INPUT_HEIGHT = "Height : "
    INPUT_AGE = "Age : "
    INPUT_DATE = "Enter date {year}: "
    # above line is for test, following lines are for real use
    RETRY_INPUT = "Invalid input, please try again: "
    Init_Reinit = "The repo is already initialized. Do you want to reinit it? (y/n)"


class HelpText(Enum):
    HELP = "Help: Use -h or --help for more information."
    VERSION = "Version: 1.0.0"
    USAGE = "Usage: python script.py [options]"
    OPTIONS = "Options: -f, -v, -h"
    EXAMPLES = "Examples: python script.py -f file.txt"
    # above line is for test, following lines are for real use
    See_More_Help = "See more help at https://github.com/Acomage/dot-cli-py"
