from enum import Enum


class OutputText(Enum):
    HELLO = "你好, {}!"
    FILE_READ = "成功读取文件{}."


class ErrorText(Enum):
    FILE_NOT_FOUND = "错误：未找到文件{}"
    INVALID_INPUT = "错误：非法输入：'{}'."
    # above line is for test, following lines are for real use
    # init
    Init_Repo_Dir_Path_Exist_But_Is_A_File = "路径{REPOPATH}是一个文件，而不是目录。"


class PromptText(Enum):
    DEFAULT = "默认值："
    INPUT_NAME = "请输入姓名："
    INPUT_HEIGHT = "请输入身高："
    INPUT_AGE = "请输入年龄："
    INPUT_DATE = "请输入日期{year}："
    RETRY_INPUT = "输入无效，请重新输入："


class HelpText(Enum):
    HELP = "帮助：使用 -h 或 --help 获取更多信息。"
    VERSION = "版本：1.0.0"
    USAGE = "用法：python script.py [选项]"
    OPTIONS = "选项：-f, -v, -h"
    EXAMPLES = "示例：python script.py -f file.txt"
    See_More_Help = "查看 https://github.com/Acomage/dot-cli-py 获取更多帮助"
    Tool_Description = "Dot：一个简单的 Linux 系统 dotfile 管理工具。"
