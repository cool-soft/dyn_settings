import logging
from typing import Any

from dynamic_settings.repository.async_settings_repository import AsyncSettingsRepository


class AsyncSettingsService:

    def __init__(self,
                 settings_repository: AsyncSettingsRepository = None,
                 settings_cache_repository: AsyncSettingsRepository = None,
                 need_to_cache_settings=True):

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._settings_repository = settings_repository
        self._settings_cache_repository = settings_cache_repository
        self._need_to_cache_settings = need_to_cache_settings

    def set_settings_repository(self, repository: AsyncSettingsRepository):
        self._logger.debug("Settings repository is set")

        self._settings_repository = repository

    def set_settings_cache_repository(self, repository: AsyncSettingsRepository):
        self._logger.debug("Settings cache repository is set")

        self._settings_cache_repository = repository

    def set_need_to_cache_settings(self, need_to_cache: bool):
        self._logger.debug(f"Need to cache is set to {need_to_cache}")

        self._need_to_cache_settings = need_to_cache

    async def get_setting_async(self, setting_name: str) -> Any:
        self._logger.debug(f"Requested setting {setting_name}")

        if self._need_to_cache_settings:
            setting_value = await self._settings_cache_repository.get_one(setting_name)
        else:
            setting_value = await self._settings_repository.get_one(setting_name)

        return setting_value

    async def set_setting_async(self, setting_name: str, setting_value: Any) -> Any:
        self._logger.debug(f"Set {setting_name} to {setting_value}")

        if self._need_to_cache_settings:
            setting_value = await self._settings_cache_repository.get_one(setting_name)
        else:
            setting_value = await self._settings_repository.get_one(setting_name)

        return setting_value
