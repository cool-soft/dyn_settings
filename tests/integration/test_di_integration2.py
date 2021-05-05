from copy import deepcopy
from datetime import datetime

import pytest
from dependency_injector import containers
from dependency_injector.providers import Singleton, Factory, Coroutine, Resource
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from dynamic_settings.di_helpers import get_one_setting
from dynamic_settings.repository.db_settings_repository import DBSettingsRepository
from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.setting_model import Setting


class Instance1:

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class Instance2:

    def __init__(self, public_instance):
        self.public_instance = public_instance


async def create_db(db_url):
    db_engine = create_async_engine(db_url)
    async with db_engine.begin() as conn:
        await conn.run_sync(Setting.metadata.drop_all)
        await conn.run_sync(Setting.metadata.create_all)
    return db_engine


class SettingsContainer(containers.DeclarativeContainer):
    db = Resource(
        create_db,
        db_url="sqlite+aiosqlite:///:memory:"
    )

    session_maker = Factory(
        orm.sessionmaker,
        autocommit=False,
        autoflush=False,
        bind=db,
        class_=AsyncSession
    )

    session_factory = Factory(orm.scoped_session, session_maker)

    settings_repository = Singleton(
        DBSettingsRepository,
        session_factory=session_factory,
        dtype_converters=[
            dtype_converters.BooleanDTypeConverter(),
            dtype_converters.DatetimeDTypeConverter(),
            dtype_converters.FloatDTypeConverter(),
            dtype_converters.IntDTypeConverter(),
            dtype_converters.StrDTypeConverter(),
            dtype_converters.NoneDTypeConverter(),
            dtype_converters.TimedeltaDTypeConverter()
        ]
    )

    instance1 = Factory(
        Instance1,
        setting_0=Coroutine(get_one_setting, settings_repository, "setting_0"),
        setting_1=Coroutine(get_one_setting, settings_repository, "setting_1"),
        setting_2=Coroutine(get_one_setting, settings_repository, "setting_2"),
    )

    instance2 = Factory(Instance2, instance1)


class TestDIIntegration2:
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
    @pytest.mark.asyncio
    async def settings_repository(self, settings_container):
        return await settings_container.settings_repository()

    # noinspection PyUnresolvedReferences
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

    # noinspection PyUnresolvedReferences
    @pytest.mark.asyncio
    async def test_injecting_instance(self,
                                      instance2_factory,
                                      settings_repository):
        await settings_repository.set_all(self.settings)
        instance2_1 = await instance2_factory()
        instance1_1 = instance2_1.public_instance
        assert instance1_1.kwargs == self.settings
