from typing import Dict, Any


class AsyncSettingsRepository:

    async def set_one(self, setting_name: str, setting_value: Any):
        raise NotImplementedError

    async def get_all(self) -> Dict[str, Any]:
        raise NotImplementedError
