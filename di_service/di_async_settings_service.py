from copy import deepcopy

from dependency_injector.providers import Configuration

from di_service.di_settings_service import DISettingsService
from repository.async_settings_repository import AsyncSettingsRepository


class DIAsyncSettingsService(DISettingsService):

    def __init__(self,
                 configuration_provider: Configuration = None,
                 settings_repository: AsyncSettingsRepository = None,
                 need_to_cache_settings=True):

        super().__init__(configuration_provider=configuration_provider,
                         need_to_cache_settings=need_to_cache_settings)

        self._settings_repository = settings_repository

    def set_settings_repository(self, settings_repository: AsyncSettingsRepository):
        self._logger.debug("Setting repository is set")
        self._settings_repository = settings_repository
        self._need_to_update_settings_cache = True

    async def update_configuration(self):
        self._logger.debug("Configuration update is requested")

        settings = await self._get_settings()
        self._configuration_provider.override(settings)

    async def _get_settings(self):
        self._logger.debug("Settings is requested")

        if self._need_to_update_settings_cache:
            self._logger.debug("Settings cache is need to update")
            await self._update_settings_cache()

        if self._need_to_cache_settings:
            self._logger.debug("Taking settings from cache")
            settings = deepcopy(self._settings_cache)

        else:
            self._logger.debug("Taking settings from repository")
            settings = await self._settings_repository.get_all()

        return settings

    async def _update_settings_cache(self):
        self._logger.debug("Cache updating requested")

        if self._need_to_update_settings_cache:
            self._logger.debug("Settings cache updating")
            self._settings_cache = await self._settings_repository.get_all()

        else:
            self._logger.debug("Settings cahce is disabled")

        self._need_to_update_settings_cache = False
