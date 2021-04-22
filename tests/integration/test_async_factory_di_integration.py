from datetime import datetime

import pytest
from dependency_injector import containers
from dependency_injector.providers import Singleton, Object, Factory

from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository
from dynamic_settings.service.simple_settings_service import SimpleSettingsService


class PublicArgsKWArgsStructure:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class SettingsContainer(containers.DeclarativeContainer):

    settings_repository = Singleton(SimpleSettingsRepository)
    default_settings = Object(None)

    settings_service = Singleton(SimpleSettingsService,
                                 settings_repository=settings_repository,
                                 defaults=default_settings)

    test_instance = Factory(
        PublicArgsKWArgsStructure,
        setting_0=settings_service.provided.get_one_setting_sync.call("setting_0"),
        setting_1=settings_service.provided.get_one_setting_sync.call("setting_1"),
        setting_2=settings_service.provided.get_one_setting_sync.call("setting_2"),
    )


class TestDSFactoryDIIntegration:

    @pytest.fixture
    def settings(self):
        return {
            "setting_0": 0,
            "setting_1": "abc",
            "setting_2": datetime.now()
        }

    @pytest.fixture
    def settings_container(self):
        return SettingsContainer()

    @pytest.fixture
    def settings_service(self, settings_container):
        settings_service = settings_container.settings_service()
        return settings_service

    @pytest.fixture
    def instance_factory(self, settings_container):
        factory = settings_container.test_instance
        return factory

    @pytest.mark.asyncio
    async def test_creating_instance(self, instance_factory, settings_service, settings):
        await settings_service.set_many_settings_async(settings)
        instance: PublicArgsKWArgsStructure = instance_factory()
        assert instance.kwargs == settings
