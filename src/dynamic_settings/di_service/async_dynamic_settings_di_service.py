import logging
from typing import Optional, Dict, Any
from copy import copy

from aiorwlock import RWLock
from dependency_injector.providers import Configuration

from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncDynamicSettingsDIService:

    def __init__(self,
                 settings_repository: Optional[SettingsRepository] = None,
                 dynamic_config: Optional[Configuration] = None,
                 configuration_lock: Optional[RWLock] = None,
                 defaults: Optional[Dict[str, Any]]=None) -> None:

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._settings_repository = settings_repository
        self._configuration = dynamic_config
        self._configuration_lock = configuration_lock
        if defaults is None:
            defaults = {}
        self._defaults = copy(defaults)

        self._logger.debug(f"Settings repository is {settings_repository}")
        self._logger.debug(f"Configuration is {dynamic_config}")
        self._logger.debug(f"Configuration lock is {configuration_lock}")
        self._logger.debug(f"Default settings {defaults}")

    def set_settings_repository(self, repository: SettingsRepository):
        self._logger.debug(f"Settings repository is set to {repository}")
        self._settings_repository = repository

    def set_dynamic_config(self, configuration: Configuration):
        self._logger.debug(f"Configuration is set to {configuration}")
        self._configuration = configuration

    def set_configuration_lock(self, lock: RWLock):
        self._logger.debug(f"Configuration lock is set to {lock}")
        self._configuration_lock = lock

    def set_defaults(self, defaults: Dict[str, Any]):
        self._logger.debug(f"Defaults are set to {defaults}")
        self._defaults = defaults

    async def set_settings(self, settings: Dict[str, Any]) -> None:
        self._logger.debug(f"Set {len(settings)} settings")

        async with self._configuration_lock.writer_lock:
            await self._settings_repository.set_many(settings)
            self._configuration.update(settings)

        self._logger.debug(f"Settings are set")

    async def initialize_repository_and_config(self):
        self._logger.debug("Initialization of repository")

        async with self._configuration_lock.writer_lock:
            current_settings = await self._settings_repository.get_all()
            new_settings = copy(self._defaults)
            new_settings.update(current_settings)
            await self._settings_repository.set_all(new_settings)
            self._configuration.update(new_settings)
