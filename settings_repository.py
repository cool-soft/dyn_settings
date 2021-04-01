from typing import Dict, Any, Callable, List


class SettingsRepository:

    def set_default_values(self, defaults: Dict[str, Any]):
        raise NotImplementedError

    def set_typing_convertors(self, convertors: Dict[str, Callable]):
        raise NotImplementedError

    def initialize_repository(self):
        raise NotImplementedError

    def is_repository_initialized(self) -> bool:
        raise NotImplementedError

    def set_one(self, setting_name: str, setting_value):
        raise NotImplementedError

    def set_many(self, settings: Dict[str, Any]):
        raise NotImplementedError

    def get_one(self, setting_name: str):
        raise NotImplementedError

    def get_all(self) -> Dict[str, Any]:
        raise NotImplementedError

    def reset_default_one(self, setting_name: str):
        raise NotImplementedError

    def reset_default_many(self, setting_names: List[str]):
        raise NotImplementedError

    def reset_default_all(self):
        raise NotImplementedError
