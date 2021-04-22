from copy import copy

import pytest

from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository
from dynamic_settings.service.simple_settings_service import SimpleSettingsService


class TestSimpleSettingsService:

    @pytest.fixture
    def settings(self):
        return {
            "setting_a": 0,
            "setting_b": 1
        }

    @pytest.fixture
    def default_settings(self):
        return {
            "setting_a": 10,
            "setting_c": False
        }

    @pytest.fixture
    def settings_repository(self):
        return SimpleSettingsRepository()

    @pytest.fixture
    def settings_service(self, default_settings, settings_repository):
        return SimpleSettingsService(
            settings_repository=settings_repository,
            defaults=default_settings
        )

    @pytest.mark.asyncio
    async def test_simple_settings_service(self,
                                           settings_service,
                                           settings_repository,
                                           settings,
                                           default_settings):

        await settings_service.initialize_service()
        await settings_service.set_many_settings_async(settings)

        combined_settings = copy(default_settings)
        combined_settings.update(settings)
        setting_names = list(combined_settings.keys())

        result_settings = await settings_repository.get_many(setting_names)
        assert combined_settings == result_settings

        result_settings2 = settings_service.get_many_settings_sync(setting_names)
        assert combined_settings == result_settings2
