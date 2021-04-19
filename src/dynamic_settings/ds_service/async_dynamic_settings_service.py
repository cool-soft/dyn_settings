import logging
from copy import copy
from typing import Optional, Dict, Any

from aiorwlock import RWLock

from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncDynamicSettingsService:

    def __init__(self,
                 settings_repository: Optional[SettingsRepository] = None,
                 settings_rwlock: Optional[RWLock] = None,
                 defaults: Optional[Dict[str, Any]] = None) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._settings_repository = settings_repository
        self._settings_rwlock = settings_rwlock
        if defaults is None:
            defaults = {}
        self._defaults = copy(defaults)

        self._logger.debug(f"Settings repository is {settings_repository}")
        self._logger.debug(f"Configuration lock is {settings_rwlock}")
        self._logger.debug(f"Default settings {defaults}")

    def set_settings_repository(self, repository: SettingsRepository):
        self._logger.debug(f"Settings repository is set to {repository}")
        self._settings_repository = repository

    def set_settings_rwlock(self, lock: RWLock):
        self._logger.debug(f"Settings rwlock is set to {lock}")
        self._settings_rwlock = lock

    def set_defaults(self, defaults: Dict[str, Any]):
        self._logger.debug(f"Defaults are set to {defaults}")
        self._defaults = defaults

    async def set_settings(self, settings: Dict[str, Any]) -> None:
        self._logger.debug(f"Set {len(settings)} settings")

        async with self._settings_rwlock.writer_lock:
            await self._settings_repository.set_many(settings)

        self._logger.debug(f"Settings are set")

    async def initialize_repository(self):
        self._logger.debug("Initialization of repository")

        async with self._settings_rwlock.writer_lock:
            current_settings = await self._settings_repository.get_all()
            new_settings = copy(self._defaults)
            new_settings.update(current_settings)
            await self._settings_repository.set_all(new_settings)
