from copy import deepcopy
from datetime import datetime

import pytest
from dependency_injector import containers
from dependency_injector.providers import Singleton, Factory, Coroutine

from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository
from dynamic_settings.repository.dict_settings_repository import DictSettingsRepository


class Instance1:

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class Instance2:

    def __init__(self, public_instance):
        self.public_instance = public_instance


async def get_setting(settings_repository: AbstractSettingsRepository, setting_name: str) -> None:
    return await settings_repository.get_one(setting_name)


class SettingsContainer(containers.DeclarativeContainer):

    settings_repository = Singleton(DictSettingsRepository)

    instance1 = Factory(
        Instance1,
        setting_0=Coroutine(get_setting, settings_repository, "setting_0"),
        setting_1=Coroutine(get_setting, settings_repository, "setting_1"),
        setting_2=Coroutine(get_setting, settings_repository, "setting_2"),
    )

    instance2 = Factory(Instance2, instance1)


class TestDIIntegration:

    settings = {
        "setting_0": 0,
        "setting_1": "abc",
        "setting_2": datetime.now()
    }

    @pytest.fixture
    def settings_container(self):
        return SettingsContainer()

    @pytest.fixture
    def instance1_factory(self, settings_container):
        return settings_container.instance1

    @pytest.fixture
    def instance2_factory(self, settings_container):
        return settings_container.instance2

    @pytest.fixture
    def settings_repository(self, settings_container):
        return settings_container.settings_repository()

    @pytest.mark.asyncio
    async def test_creating_instance(self,
                                     instance1_factory,
                                     settings_repository):

        await settings_repository.set_many(self.settings)
        instance1_1: Instance1 = await instance1_factory()
        assert instance1_1.kwargs == self.settings

        updated_settings = deepcopy(self.settings)
        # noinspection PyTypeChecker
        updated_settings["setting_2"] = 10.5
        await settings_repository.set_many(updated_settings)
        instance1_2: Instance1 = await instance1_factory()
        assert instance1_2.kwargs == updated_settings
        assert instance1_1.kwargs != updated_settings

    @pytest.mark.asyncio
    async def test_injecting_instance(self,
                                      instance2_factory,
                                      settings_repository):
        await settings_repository.set_all(self.settings)
        instance2_1 = await instance2_factory()
        instance1_1 = instance2_1.public_instance
        assert instance1_1.kwargs == self.settings
