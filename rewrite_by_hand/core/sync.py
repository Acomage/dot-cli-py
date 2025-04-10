from rewrite_by_hand.utils.blocks import blocks_manager
from rewrite_by_hand.core.config import ConfigManager


class SyncManager:
    def __init__(self, if_hook=False):
        self.config_manager = ConfigManager(if_hook=if_hook)

    def sync(self, path_str: str) -> None:
        pass

    def apply(self, path_str: str) -> None:
        pass

    def sync_all(self) -> None:
        pass

    def apply_all(self) -> None:
        pass
