from typing import Dict, Any, List


class SettingsService:

    async def set_one_settings_async(self, setting_name: str, setting_value: Any) -> None:
        raise NotImplementedError

    async def set_many_settings_async(self, settings: Dict[str, Any]) -> None:
        raise NotImplementedError

    def get_one_setting_sync(self, setting_name: str) -> Any:
        raise NotImplementedError

    def get_many_settings_sync(self, settings_names: List[str]) -> Dict[str, Any]:
        raise NotImplementedError

    async def initialize_service(self):
        raise NotImplementedError
