import importlib
import sys
from types import ModuleType
from typing import Any, Callable, Optional
from rewrite_by_hand.data.variables import DEFAULT_LANGUAGE, MESSAGES_PATH


class OutputManager:
    def __init__(
        self, lang: str = DEFAULT_LANGUAGE, fallback_lang: str = DEFAULT_LANGUAGE
    ):
        """
        :param lang: 目标语言代码 (如 "en"/"zh")
        :param fallback_lang: 回退语言代码
        """
        self.lang = lang
        self.fallback_lang = fallback_lang
        self._message_modules = {
            "output": None,
            "error": None,
            "prompt": None,
            "help": None,
        }
        self._load_language()

    def _load_language(self):
        """动态加载语言模块（更新校验逻辑）"""
        # ...保持原有加载逻辑不变...
        # 更新验证模块结构

        def try_import(lang: str) -> Optional[ModuleType]:
            try:
                return importlib.import_module(f"{MESSAGES_PATH}.{lang}")
            except ImportError:
                return None

        # 优先加载目标语言
        target_module = try_import(self.lang)

        # 回退逻辑
        if not target_module:
            target_module = try_import(self.fallback_lang)
            print(
                f"Warning: language module: {self.lang} not found, falling back to {self.fallback_lang}",
                file=sys.stderr,
            )
            if not target_module:
                raise ImportError(
                    f"Can not load language module: {self.lang} and {self.fallback_lang}"
                )

        self._message_modules.update(
            {
                "output": getattr(target_module, "OutputText", None),
                "error": getattr(target_module, "ErrorText", None),
                "prompt": getattr(target_module, "PromptText", None),  # 新增
                "help": getattr(target_module, "HelpText", None),  # 新增
            }
        )

        if None in self._message_modules.values():
            raise ValueError(f"Invalid language module structure: {self.lang}")

    def out(self, key: str, *args, **kwargs):
        """输出普通信息到 stdout"""
        self._print("output", key, sys.stdout, *args, **kwargs)

    def err(self, key: str, *args, **kwargs):
        """输出错误信息到 stderr"""
        self._print("error", key, sys.stderr, *args, **kwargs)
        self._print("help", "See_More_Help", sys.stderr, *args, **kwargs)

    def _print(self, msg_type: str, key: str, stream, *args, **kwargs):
        """通用打印方法"""
        enum_cls = self._message_modules[msg_type]

        # 获取消息模板
        try:
            message = getattr(enum_cls, key).value
        except AttributeError:
            message = f"[MISSING KEY] {key} of {msg_type}"

        # 格式化消息
        try:
            formatted = message.format(*args, **kwargs)
        except (IndexError, KeyError):
            formatted = f"[FORMAT ERROR] {message} with {args} and {kwargs}"

        print(formatted, file=stream)

    def prompt(
        self,
        key: str,
        *args,
        default: Optional[Any] = None,
        validator: Optional[Callable[[str], bool]] = None,
        **kwargs,
    ) -> str:
        """
        获取本地化输入提示
        :param key: 消息键
        :param default: 默认值（支持任意类型）
        :param validator: 输入验证函数
        :return: 用户输入的内容
        """
        # 获取提示模板
        enum_cls = self._message_modules["prompt"]
        try:
            prompt_text = getattr(enum_cls, key).value
        except AttributeError:
            prompt_text = f"[MISSING KEY] {key} of prompt"

        # 处理默认值显示逻辑
        if default is not None:
            try:
                default_text = getattr(enum_cls, "DEFAULT").value
            except AttributeError:
                default_text = "default value: "
            prompt_text += f" ({default_text}{default}):"

        # 格式化提示信息
        try:
            formatted_prompt = prompt_text.format(*args, **kwargs)
        except (IndexError, KeyError):
            formatted_prompt = f"[FORMAT ERROR] {prompt_text} with {args} and {kwargs}"

        # 构建完整提示（包含重试逻辑）
        retry_prompt = self._get_message("prompt", "RETRY_INPUT", default=">>> ")

        while True:
            user_input = input(formatted_prompt).strip()

            # 处理空输入和默认值
            if not user_input and default is not None:
                return default

            # 执行自定义验证
            if validator and not validator(user_input):
                print(retry_prompt)
                continue

            return user_input

    # 新增辅助方法
    def _get_message(
        self, msg_type: str, key: str, default: Optional[str] = None
    ) -> str:
        """安全获取消息模板"""
        enum_cls = self._message_modules[msg_type]
        try:
            return getattr(enum_cls, key).value
        except AttributeError:
            return default or f"[MISSING KEY] {key} of {msg_type}"


output_manager = OutputManager()


def validate_yes_no(input_str: str) -> bool:
    return input_str.lower() in ["y", "n"]


def validate_yes_no_all(input_str: str) -> bool:
    return input_str.lower() in ["y", "n", "a"]


if __name__ == "__main__":
    manager = OutputManager(lang="zh")

    # 基础输入
    name = manager.prompt("INPUT_NAME")
    # 显示：请输入姓名：

    # 带默认值和格式化
    age = manager.prompt("INPUT_AGE", default=18)
    # 显示：请输入年龄（默认18）：

    # 带类型验证
    def validate_int(input_str):
        try:
            int(input_str)
            return True
        except ValueError:
            return False

    height = manager.prompt("INPUT_HEIGHT", default=170, validator=validate_int)
    # 显示：请输入身高（默认170）：
    # 如果输入非数字会显示：输入无效，请重新输入：

    # 复杂格式
    date = manager.prompt("INPUT_DATE", year=2023, default="2023-01-01")
    print(f"name: {name},\nage: {age},\nheight: {height},\ndate: {date}")
