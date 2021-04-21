from copy import copy

import pytest
from aiorwlock import RWLock

from dynamic_settings.ds_service.async_dynamic_settings_service import AsyncDynamicSettingsService
from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository


class TestDynamicSettingsService:

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
    async def settings_rwlock(self):
        return RWLock()

    # noinspection PyTypeChecker
    @pytest.fixture
    async def settings_service(self, default_settings, settings_rwlock, settings_repository):
        return AsyncDynamicSettingsService(
            settings_repository=settings_repository,
            settings_rwlock=settings_rwlock,
            defaults=default_settings
        )

    # noinspection PyUnresolvedReferences
    @pytest.mark.asyncio
    async def test_dynamic_settings_di_service(self,
                                               settings_service,
                                               settings_repository,
                                               settings,
                                               default_settings,
                                               settings_rwlock):

        await settings_service.initialize_repository()
        await settings_service.set_settings(settings)

        combined_settings = copy(default_settings)
        combined_settings.update(settings)
        setting_names = list(combined_settings.keys())

        async with settings_rwlock.reader_lock:
            result_settings = await settings_repository.get_many(setting_names)
        assert combined_settings == result_settings

        async with settings_rwlock.reader_lock:
            result_settings2 = await settings_service.get_settings(setting_names)
        assert combined_settings == result_settings2
