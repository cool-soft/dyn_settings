import logging

from dependency_injector.providers import Configuration


class DISettingsService:

    def __init__(self,
                 configuration_provider: Configuration = None,
                 need_to_cache_settings=True):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance of the service")

        self._configuration_provider = configuration_provider

        self._cached_settings = None
        self._need_to_update_settings_cache = True
        self._need_to_cache_settings = need_to_cache_settings

    def set_configuration_provider(self, configuration_provider: Configuration):
        self._logger.debug("Configuration provider is set")
        self._configuration_provider = configuration_provider

    def set_need_to_cache_settings(self, need_to_cache: bool):
        self._logger.debug(f"Need to cache is set to {need_to_cache}")
        self._need_to_cache_settings = need_to_cache
