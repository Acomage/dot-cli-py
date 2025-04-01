from enum import Enum


class OutputText(Enum):
    HELLO = "你好, {}!"
    FILE_READ = "成功读取文件{}."


class ErrorText(Enum):
    FILE_NOT_FOUND = "错误：未找到文件{}"
    INVALID_INPUT = "错误：非法输入：'{}'."


class PromptText(Enum):
    INPUT_NAME = "请输入姓名："
    INPUT_AGE = "请输入年龄（默认{default_age}）："
    RETRY_INPUT = "输入无效，请重新输入："
