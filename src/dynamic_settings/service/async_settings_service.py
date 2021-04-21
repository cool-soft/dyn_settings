import logging
from copy import copy
from typing import Optional, Dict, Any, List

from aiorwlock import RWLock

from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncSettingsService:

    def __init__(self,
                 settings_repository: Optional[SettingsRepository] = None,
                 defaults: Optional[Dict[str, Any]] = None) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._settings_repository = settings_repository
        self.__settings_lock = None
        if defaults is None:
            defaults = {}
        self._defaults = copy(defaults)

        self._logger.debug(f"Settings settings_repository is {settings_repository}")
        self._logger.debug(f"Default settings {defaults}")

    def set_settings_repository(self, repository: SettingsRepository) -> None:
        self._logger.debug(f"Settings settings_repository is set to {repository}")
        self._settings_repository = repository

    def set_defaults(self, defaults: Dict[str, Any]):
        self._logger.debug(f"Defaults are set to {defaults}")
        self._defaults = defaults

    async def set_settings(self, settings: Dict[str, Any]) -> None:
        self._logger.debug(f"Set {len(settings)} settings")

        settings_lock = await self.get_settings_lock()
        async with settings_lock.writer_lock:
            await self._settings_repository.set_many(settings)

        self._logger.debug(f"Settings are set")

    async def get_settings(self, settings_names: List[str]) -> Dict[str, Any]:
        self._logger.debug(f"Requested settings: {settings_names}")

        settings_lock = await self.get_settings_lock()
        async with settings_lock.writer_lock:
            settings = await self._settings_repository.get_many(settings_names)

        self._logger.debug(f"Settings are get")
        return settings

    async def initialize_repository(self):
        self._logger.debug("Initialization of settings_repository")

        settings_lock = await self.get_settings_lock()
        async with settings_lock.writer_lock:
            current_settings = await self._settings_repository.get_all()
            new_settings = copy(self._defaults)
            new_settings.update(current_settings)
            await self._settings_repository.set_all(new_settings)

    async def get_settings_lock(self) -> RWLock:
        self._logger.debug("Settings RWLock is requested")

        if self.__settings_lock is None:
            self._logger.debug("Creating settings rwlock")
            self.__settings_lock = RWLock()

        return self.__settings_lock
