import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, AsyncSession
from sqlalchemy.orm import sessionmaker

from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.async_db_settings_repository import AsyncDBSettingsRepository
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter
from dynamic_settings.repository.di_integration import async_db_settings_provider


class TestAsyncSettingsDBDIIntegration:

    @pytest.fixture
    def samples(self):
        return {
            "setting_0": None,
            "setting_1": True,
            "setting_2": False,
            "setting_3": 10,
            "setting_4": 50.23,
            "setting_5": "string value",
            "setting_6": datetime.now(),
            "setting_7": timedelta(seconds=123.45)
        }

    @pytest.fixture
    def converters(self):
        converters = [
            dtype_converters.BooleanDTypeConverter(),
            dtype_converters.DatetimeDTypeConverter(),
            dtype_converters.FloatDTypeConverter(),
            dtype_converters.IntDTypeConverter(),
            dtype_converters.StrDTypeConverter(),
            dtype_converters.NoneDTypeConverter(),
            dtype_converters.TimedeltaDTypeConverter()
        ]
        return converters

    db_url = "sqlite+aiosqlite:///:memory:"

    @pytest_asyncio.fixture
    async def session_factory(self):
        engine = create_async_engine(self.db_url)
        async with engine.begin() as conn:
            await conn.run_sync(Setting.metadata.drop_all)
            await conn.run_sync(Setting.metadata.create_all)
            await conn.commit()
        db_session_maker = sessionmaker(
            expire_on_commit=False,
            bind=engine,
            class_=AsyncSession
        )
        session_factory = async_scoped_session(
            db_session_maker,
            scopefunc=asyncio.current_task
        )
        return session_factory

    @pytest_asyncio.fixture
    async def repository(self, session_factory, converters):
        return AsyncDBSettingsRepository(session_factory, SettingsConverter(converters))

    @pytest.mark.asyncio
    async def test_di_integrator(self, session_factory, repository, samples):
        async with session_factory.begin() as session:
            await repository.set_many(samples)
            await session.commit()
        for setting_name, setting_value in samples.items():
            assert setting_value == await async_db_settings_provider(
                session_factory,
                repository,
                setting_name,
                remove_session_after_use=False
            )
        await session_factory.remove()
