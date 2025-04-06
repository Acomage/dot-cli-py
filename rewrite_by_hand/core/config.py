from typing import Tuple
import sys
from rewrite_by_hand.utils.file_system import FileSystem, Owner
from rewrite_by_hand.cli.output import output_manager
from rewrite_by_hand.data.variables import REPO_CONFIG_PATH, REPO_LOCAL_CONFIG_PATH


class ConfigManager:
    def __init__(self, if_hook=False):
        self.if_hook = if_hook
        self.config = FileSystem(if_hook=if_hook)
        self.local_config = FileSystem(if_hook=False, local=True)

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
        match self.local_config.if_exists(path_str):
            case True, _:
                self.local_config.remove(path_str)
            case False, _:
                output_manager.err(
                    "Path_Does_Not_Contain_Local_Config",
                    path=path_str,
                )
                sys.exit(1)

    def add(self, path_str: str, owner: Owner) -> None:
        self.pure_add(path_str, owner)
        self.manage(path_str)

    def remove(self, path_str: str) -> None:
        self.unmanage(path_str)
        self.pure_remove(path_str)

    def manage_software(self, software: Owner) -> None:
        flag = True
        for super_forests in self.config.forest:
            for super_forest in super_forests:
                for top_tree, owner in super_forest:
                    if owner == software:
                        flag = False
                        match self.local_config.if_exists(top_tree.path.path):
                            case True, _:
                                pass
                            case False, _:
                                self.local_config.add(top_tree.path.path, owner)
        if flag:
            output_manager.err(
                "Do_Not_Have_Software",
                software=software,
            )
            sys.exit(1)

    def unmanage_software(self, software: Owner) -> None:
        flag = True
        for super_forests in self.local_config.forest:
            for super_forest in super_forests:
                for top_tree, owner in super_forest:
                    if owner == software:
                        flag = False
                        self.local_config.remove(top_tree.path.path)
        if flag:
            output_manager.err(
                "Do_Not_Have_Software_Under_Manage",
                software=software,
            )
            sys.exit(1)

    @classmethod
    def from_json(
        cls, config_json_str: str, local_config_json_str: str, if_hook: bool = False
    ) -> "ConfigManager":
        config_manager = cls()
        config_manager.config = FileSystem.from_json(config_json_str, if_hook=if_hook)
        config_manager.local_config = FileSystem.from_json(
            local_config_json_str, if_hook=False, local=True
        )
        return config_manager

    def to_json(self) -> Tuple[str, str]:
        config_json_str = self.config.to_json()
        local_config_json_str = self.local_config.to_json()
        return config_json_str, local_config_json_str

    @classmethod
    def load(cls, if_hook: bool = False) -> "ConfigManager":
        try:
            with open(REPO_CONFIG_PATH, "r") as config_file:
                config_json_str = config_file.read()
        except FileNotFoundError:
            output_manager.err("Can_Not_Load_Config")
            sys.exit(1)
        try:
            with open(REPO_LOCAL_CONFIG_PATH, "r") as local_config_file:
                local_config_json_str = local_config_file.read()
        except FileNotFoundError:
            output_manager.err("Can_Not_Load_Local_Config")
            sys.exit(1)
        return cls.from_json(config_json_str, local_config_json_str, if_hook=if_hook)

    def save(self) -> None:
        config_json_str, local_config_json_str = self.to_json()
        try:
            with open(REPO_CONFIG_PATH, "w") as config_file:
                config_file.write(config_json_str)
        except PermissionError:
            output_manager.err(
                "Can_Not_Save_Config",
            )
            sys.exit(1)
        try:
            with open(REPO_LOCAL_CONFIG_PATH, "w") as local_config_file:
                local_config_file.write(local_config_json_str)
        except PermissionError:
            output_manager.err(
                "Can_Not_Save_Local_Config",
            )
            sys.exit(1)
