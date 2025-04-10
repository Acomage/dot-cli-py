from enum import Enum


class OutputText(Enum):
    HELLO = "Hello, {}!"
    FILE_READ = "File {} read successfully."
    # above line is for test, following lines are for real use
    # init
    Init_Cloning = "Cloning repository from {Url}..."
    Init_Cloning_Success = "Cloning repository from {Url} success."
    Init_Success = "Repo initialization successfully. Have a nice day!"
    Init_Next_Step = "Next step: You can\n1. run 'dot add <path> <software>' to manage your dotfiles\n2. run 'dot remote <url>' to set a remote repository."
    # clean
    Clean_Success = "Cleaned {REPOPATH} successfully."
    # add
    Add_Success = "Added {path} for {owner} successfully."
    # manage
    Manage_Success = "Managed {path} successfully."
    Manage_All_Success = "Managed all files successfully."
    Manage_software_Success = "Managed {software} successfully."
    # remove
    Remove_Success = "Removed {path} successfully."
    # unmanage
    Unmanage_Success = "Unmanaged {path} successfully."
    Unmanage_All_Success = "Unmanaged all files successfully."
    Unmanage_software_Success = "Unmanaged {software} successfully."
    # remote
    Remote_Set_Success = "Set remote URL to {url} successfully."
    Remote_Remove_Success = "Removed remote URL successfully."
    # push
    Push_Success = "Pushed to remote repository successfully."
    # pull
    Pull_Success = "Pulled from remote repository successfully."


class ErrorText(Enum):
    FILE_NOT_FOUND = "Error: File {} not found!"
    INVALID_INPUT = "Error: Invalid input '{}'."
    # above line is for test, following lines are for real use
    # fs_utils
    Ensure_Dir_Exists_Failed = "Error creating directory: {path} with error: {error}"
    # fs_type
    Path_Not_Exist = "Error: The path {path} does not exist."
    Use_Path_Contain_REPOPATH = "Error: You cannot use a path containing the {REPOPATH} or there is a recursive error."
    File_Is_A_Dir = "Error: The path {path} is a directory, not a file."
    Dir_Is_A_File = "Error: The path {path} is a file, not a directory."
    Permission_Denied = "Error: Permission denied for {path}."
    # retree
    Retree_Failed = "Error: Retree failed with error: {error} when deleting {path}"
    # health
    Repo_Not_Healthy = "The repo is not healthy. Maybe you can buck to the last commit."
    # git
    Add_Commit_Failed = "Git failed to add and commit the changes. Error: {error}, You should do that manually."
    Run_Remote_Failed = "Git failed to run the remote command. Error: {error}, You should do that manually."
    # init
    Init_Repo_Dir_Path_Exist_But_Is_A_File = "The path {REPOPATH} is a file, not a directory. If you need that file, you can set another path as repo path."
    Init_Repo_Dir_Exist_But_Not_Our_Repo = "We find that there is not a correct REAMDE.md file in {REPOPATH}. It may means that {REPOPATH} is created by other tools. If you need that directory, you can set another path as repo path."
    Init_Clean_Failed = "Failed to clean the directory {REPOPATH}. Error: {error}"
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
    # clean
    Clean_Repo_Dir_Path_Not_Exist = "The path {REPOPATH} does not exist. If you have initialized a repo without cleaning it and changed the path, you can remove the old repo manually."
    Clean_Repo_Dir_Exist_But_Not_Our_Repo = "The path {REPOPATH} seems not generated by Dot. You should check if you need it and delete it if not."
    Clean_Abort = "Aborting clean command."
    # hook
    Hooker_Add_File_Failed = "Permission denied for copy {path}."
    Hooker_Remove_Failed = "Failed to remove {path} with error: {error}"
    Hooker_Remove_Failed_File_Not_Found = "You are trying to remove a file or directory {path} that does not exist in the repo. This error would never happen if your repo is healthy. Please check if your repo is healthy by running 'dot check'."
    # file_system
    File_Already_Managed = "The path {path} is already managed."
    File_Already_Exists = "Path {path} already exists in repo, maybe you want to use `dot manage` instead of `dot add`"
    Super_Dir_With_Differnet_Owner = (
        "There exists a super directory of {path} with a different owner: {owner}"
    )
    Sub_Dir_With_Different_Owner = (
        "There exists a sub directory of {path} with a different owner: {owner}"
    )
    Sub_File_With_Different_Owner = (
        "There exists a sub file of {path} with a different owner: {owner}"
    )
    Path_Not_Found = "Path {path} is not found in repo."
    # add
    Add_Should_Init = (
        "You have not initialized a repo yet. Please run 'dot init' first."
    )
    # config
    Path_Does_Not_Contain_Config = "The file or directory {path} does not contain in the config.json file. You should run 'dot add' first."
    Path_Does_Not_Contain_Local_Config = "The file or directory {path} does not contain in the local_config.json file. You should run 'dot manage' first."
    Can_Not_Load_Config = (
        "Can not load config.json. Please check if the file exists and is valid JSON."
    )
    Can_Not_Load_Local_Config = "Can not load local_config.json. Please check if the file exists and is valid JSON."
    Can_Not_Save_Config = (
        "Can not save config.json. Please check if the file is writable."
    )
    Can_Not_Save_Local_Config = (
        "Can not save local_config.json. Please check if the file is writable."
    )
    # manage
    Do_Not_Have_Software = "You do not have a software named {software} in the repo."
    Do_Not_Have_Software_Under_Manage = (
        "You do not have a software named {software} under managed."
    )
    # remote
    Remote_Remove_Failed = "Failed to remove remote URL. Error: {error}"
    Remote_Set_Failed = "Failed to set remote URL. Error: {error}"
    No_Remote_To_Remove = "No remote to remove."
    # push
    Do_Not_Have_Remote = "You do not have a remote repository yet. Please run 'dot remote <url>' to set a remote repository."
    Push_Failed = "Failed to push to remote repository. Error: {error}"
    # pull
    Pull_Failed = "Failed to pull from remote repository. Error: {error}"
    Fetch_Failed = "Failed to fetch from remote repository. Error: {error}"
    Reset_Failed = "Failed to soft reset the repository to remote. Error: {error}"
    # blocks
    Unclosed_Block = "Unclosed block(s) detected: {unclosed_str}"
    Unopened_Block = "End marker(s) without matching start: {unopened_str}"
    Nested_Block = "Nested block detected: '{mark}' on line {line_num} is nested inside '{parent_mark}' which started on line {parent_line}"
    Not_Matching_Block = "Unexpected end marker: '{mark}' on line {line_num} has no matching start marker"
    Missmatched_Block = "Mismatched block markers on line {line_num}: Expected end of '{last_mark}' (from line {start_line}) but found '{mark}'"
    Block_Not_Found = (
        "Block not found: There is no block mark with '{mark}' in the file."
    )


class PromptText(Enum):
    DEFAULT = "Default: "
    INPUT_NAME = "Enter your name: "
    INPUT_HEIGHT = "Height : "
    INPUT_AGE = "Age : "
    INPUT_DATE = "Enter date {year}: "
    # above line is for test, following lines are for real use
    RETRY_INPUT = "Invalid input, please try again: "
    # init
    Init_Reinit = "The repo is already initialized. Do you want to reinit it? (y/n)"
    # clean
    Clean_Confirm = "Are you sure you want to clean the repo{REPOPATH}? (y/n)"


class HelpText(Enum):
    HELP = "Help: Use -h or --help for more information."
    VERSION = "Version: 1.0.0"
    USAGE = "Usage: python script.py [options]"
    OPTIONS = "Options: -f, -v, -h"
    EXAMPLES = "Examples: python script.py -f file.txt"
    # above line is for test, following lines are for real use
    See_More_Help = "See more help at https://github.com/Acomage/dot-cli-py"
    Tool_Description = "Dot: A simple dotfile management tool for Linux systems."
    Subparser_Description = "Subcommands for Dot."
    Init_Description = "Initialize a dotfiles repository."
    Init_Url_Description = "URL of the remote repository to clone."
