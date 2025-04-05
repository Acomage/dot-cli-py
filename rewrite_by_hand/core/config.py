from typing import Tuple
import sys
from rewrite_by_hand.utils.file_system import FileSystem, Owner
from rewrite_by_hand.utils.fs_type import Path
from rewrite_by_hand.cli.output import output_manager


class ConfigManager:
    def __init__(self, if_hook=False):
        self.if_hook = if_hook
        self.config = FileSystem(if_hook=if_hook)
        self.local_config = FileSystem(if_hook=if_hook)

    def pure_add(self, path_str: str, owner: Owner) -> None:
        self.config.add(path_str, owner)

    def pure_remove(self, path_str: str) -> None:
        self.config.remove(path_str)

    def manage(self, path_str: str) -> None:
        match self.config.if_exists(path_str):
            case True, owner:
                self.local_config.add(path_str, owner)
            case False, _:
                output_manager.err(
                    "Path_Does_Not_Contain_Config",
                    path=path_str,
                )
                sys.exit(1)

    def unmanage(self, path_str: str) -> None:
        pass

    def add(self, path_str: str, owner: Owner) -> None:
        self.pure_add(path_str, owner)
        self.manage(path_str)

    def remove(self, path_str: str) -> None:
        self.pure_remove(path_str)
        self.unmanage(path_str)

    # @classmethod
    # def from_json(
    #     cls, config_json_str: str, local_config_json_str: str
    # ) -> "ConfigManager":
    #     pass
    #
    # def to_json(self) -> Tuple[str, str]:
    #     pass
    #
    # @classmethod
    # def load(cls, if_hook: bool = False) -> "ConfigManager":
    #     pass
    #
    # def save(self) -> None:
    #     pass
