from typing import Dict, Any


class SyncSettingsRepository:

    def set_one(self, setting_name: str, setting_value: Any):
        raise NotImplementedError

    def get_all(self) -> Dict[str, Any]:
        raise NotImplementedError
