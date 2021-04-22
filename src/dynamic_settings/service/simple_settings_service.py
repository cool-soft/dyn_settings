import logging
import threading
from copy import copy
from typing import Optional, Dict, Any, List

from dynamic_settings.service.settings_service import SettingsService

from dynamic_settings.repository.settings_repository import SettingsRepository


class SimpleSettingsService(SettingsService):

    def __init__(self,
                 settings_repository: Optional[SettingsRepository] = None,
                 defaults: Optional[Dict[str, Any]] = None) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._settings_repository = settings_repository
        if defaults is None:
            defaults = {}
        self._defaults = copy(defaults)

        self._settings_lock = threading.Lock()
        self._settings_sync_cache = {}

        self._logger.debug(f"Settings settings_repository is {settings_repository}")
        self._logger.debug(f"Default settings {defaults}")

    def set_settings_repository(self, repository: SettingsRepository) -> None:
        self._logger.debug(f"Settings settings_repository is set to {repository}")
        self._settings_repository = repository

    def set_defaults(self, defaults: Dict[str, Any]):
        self._logger.debug(f"Defaults are set to {defaults}")
        self._defaults = defaults

    async def set_one_settings_async(self, setting_name: str, setting_value: Any) -> None:
        self._logger.debug(f"Set {setting_name} = {setting_value} async")
        with self._settings_lock:
            await self._settings_repository.set_one(setting_name, setting_value)
            self._settings_sync_cache[setting_name] = setting_value
        self._logger.debug(f"Setting is set async")

    async def set_many_settings_async(self, settings: Dict[str, Any]) -> None:
        self._logger.debug(f"Set {len(settings)} settings async")
        with self._settings_lock:
            await self._settings_repository.set_many(settings)
            for setting_name, setting_value in settings.items():
                self._settings_sync_cache[setting_name] = setting_value
        self._logger.debug(f"Settings are set async")

    def get_one_setting_sync(self, setting_name: str) -> Any:
        self._logger.debug(f"Requested setting sync: {setting_name}")
        with self._settings_lock:
            setting_value = self._settings_sync_cache.get(setting_name)
        self._logger.debug(f"Settings are get sync")
        return setting_value

    def get_many_settings_sync(self, settings_names: List[str]) -> Dict[str, Any]:
        self._logger.debug(f"Requested settings sync: {settings_names}")
        with self._settings_lock:
            settings = {}
            for name in settings_names:
                settings[name] = self._settings_sync_cache.get(name)
        self._logger.debug(f"Settings are get sync")
        return settings

    async def initialize_service(self):
        self._logger.debug("Initialization of settings service")
        with self._settings_lock:
            current_settings = await self._settings_repository.get_all()
            new_settings = copy(self._defaults)
            new_settings.update(current_settings)
            await self._settings_repository.set_all(new_settings)
            self._settings_sync_cache = new_settings
