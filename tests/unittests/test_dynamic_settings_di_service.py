from copy import copy

import pytest
from aiorwlock import RWLock
from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer
from dynamic_settings.repository.db_settings_repository import dtype_converters, DBSettingsRepository
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session

from dynamic_settings.di_service.async_dynamic_settings_di_service import AsyncDynamicSettingsDIService
from dynamic_settings.repository.db_settings_repository.setting_model import Setting


async def instant_db_settings_schema(db_engine):
    async with db_engine.begin() as conn:
        await conn.run_sync(Setting.metadata.drop_all)
        await conn.run_sync(Setting.metadata.create_all)


class SettingsContainer(DeclarativeContainer):

    db_engine = providers.Resource(create_async_engine,
                                   url=providers.Object("sqlite+aiosqlite:///:memory:"))

    session_maker = providers.Singleton(sessionmaker,
                                        autocommit=providers.Object(False),
                                        autoflush=providers.Object(False),
                                        bind=db_engine,
                                        class_=providers.Object(AsyncSession))

    session_factory = providers.Singleton(scoped_session,
                                          session_factory=session_maker)

    converters = providers.List(
        providers.Factory(dtype_converters.BooleanDTypeConverter),
        providers.Factory(dtype_converters.DatetimeDTypeConverter),
        providers.Factory(dtype_converters.FloatDTypeConverter),
        providers.Factory(dtype_converters.IntDTypeConverter),
        providers.Factory(dtype_converters.StrDTypeConverter),
        providers.Factory(dtype_converters.NoneDTypeConverter),
        providers.Factory(dtype_converters.TimedeltaDTypeConverter)
    )

    settings_repository = providers.Singleton(
        DBSettingsRepository,
        session_factory=session_factory,
        dtype_converters=converters
    )

    dynamic_config = providers.Configuration()
    dynamic_config_rwlock = providers.Singleton(RWLock)
    defaults = providers.Configuration()

    settings_service = providers.Singleton(AsyncDynamicSettingsDIService,
                                           settings_repository=settings_repository,
                                           dynamic_config=dynamic_config.provider,
                                           configuration_lock=dynamic_config_rwlock,
                                           defaults=defaults)


class TestDynamicSettingsDIService:

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
    def settings_pkg(self, default_settings):
        container = SettingsContainer()
        container.defaults.from_dict(default_settings)
        return container

    @pytest.mark.asyncio
    async def test_dynamic_settings_di_service(self, settings_pkg, settings, default_settings):
        db_engine = settings_pkg.db_engine()
        await instant_db_settings_schema(db_engine)

        settings_service: AsyncDynamicSettingsDIService = settings_pkg.settings_service()
        await settings_service.initialize_repository_and_config()
        await settings_service.set_settings(settings)

        combined_settings = copy(default_settings)
        combined_settings.update(settings)

        result_settings = {}
        lock: RWLock = settings_pkg.dynamic_config_rwlock()
        async with lock.reader_lock:
            for setting_name in combined_settings.keys():
                result_settings[setting_name] = settings_pkg.dynamic_config.get(setting_name)

        assert combined_settings == result_settings
