import logging
from typing import Optional, Dict, Any

from aiorwlock import RWLock
from dependency_injector.providers import Configuration

from dynamic_settings.repository.settings_repository import SettingsRepository


class AsyncDynamicSettingsDIService:

    def __init__(self,
                 settings_repository: Optional[SettingsRepository] = None,
                 configuration: Optional[Configuration] = None,
                 configuration_lock: Optional[RWLock] = None) -> None:

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._settings_repository = settings_repository
        self._configuration = configuration
        self._configuration_lock = configuration_lock

        self._logger.debug(f"Settings repository is {settings_repository}")
        self._logger.debug(f"Configuration is {configuration}")
        self._logger.debug(f"Configuration lock is {configuration_lock}")

    def set_settings_repository(self, repository: SettingsRepository):
        self._logger.debug(f"Settings repository is set to {repository}")
        self._settings_repository = repository

    def set_configuration(self, configuration: Configuration):
        self._logger.debug(f"Configuration is set to {configuration}")
        self._configuration = configuration

    def set_configuration_lock(self, lock: RWLock):
        self._logger.debug(f"Configuration lock is set to {lock}")
        self._configuration_lock = lock

    async def set_settings(self, settings: Dict[str, Any]) -> None:
        self._logger.debug(f"Set {len(settings)} settings")

        async with self._configuration_lock.writer_lock:
            await self._settings_repository.set_many(settings)
            self._configuration.update(settings)

        self._logger.debug(f"Settings are set")
