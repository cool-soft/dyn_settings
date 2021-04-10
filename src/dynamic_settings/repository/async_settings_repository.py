from typing import Any, Dict


class AsyncSettingsRepository:

    async def set_one(self, setting_name: str, setting_value: Any) -> None:
        raise NotImplementedError

    async def get_one(self, setting_name: str) -> Any:
        raise NotImplementedError

    async def get_all(self) -> Dict[str, Any]:
        raise NotImplementedError

    async def set_all(self, settings: Dict[str, Any]) -> None:
        raise NotImplementedError
