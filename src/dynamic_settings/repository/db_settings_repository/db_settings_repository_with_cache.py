import logging
from copy import copy
from typing import Any, Dict, List, Optional, Callable, Iterator

from sqlalchemy.future import select

from . import DBSettingsRepository
from .dtype_converters import DTypeConverter
from .setting_model import Setting


class DBSettingsRepositoryWithCache(DBSettingsRepository):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._settings_cache: Dict[str, Any] = {}
        self._need_to_update_cache = True

    async def get_one(self, setting_name: str) -> Any:
        self._logger.debug(f"Requested setting {setting_name}")

        if self._need_to_update_cache:
            await self._update_cache()

        settings = self._settings_cache.get(setting_name)
        return settings

    async def set_one(self, setting_name: str, setting_value: Any) -> None:
        await super().set_one(setting_name, setting_value)
        self._settings_cache[setting_name] = setting_value

    async def get_many(self, setting_names: List[str]) -> Dict[str, Any]:
        self._logger.debug(f"Requested settings: {setting_names}")

        if self._need_to_update_cache:
            await self._update_cache()

        settings = {}
        for setting_name in setting_names:
            settings[setting_name] = self._settings_cache.get(setting_name)

        return settings

    async def set_many(self, settings: Dict[str, Any]) -> None:
        await super().set_many(settings)

        for setting_name, setting_value in settings.items():
            self._settings_cache[setting_name] = setting_value

    async def get_all(self) -> Dict[str, Any]:
        self._logger.debug("All settings are requested")

        if self._need_to_update_cache:
            await self._update_cache()

        settings = copy(self._settings_cache)
        return settings

    async def set_all(self, settings: Dict[str, Any]) -> None:
        await super().set_all(settings)
        self._settings_cache = copy(settings)

    async def _update_cache(self):
        self._logger.debug("Updating cache")
        self._settings_cache = await super().get_all()
        self._need_to_update_cache = False
