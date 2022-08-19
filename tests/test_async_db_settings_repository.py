import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session

from dynamic_settings.repository.db_settings_repository.async_db_settings_repository import AsyncDBSettingsRepository
from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter


class TestAsyncDBSettingsRepositoryBaseOperations:

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
    def samples_2(self):
        return {
            "setting_20": 1,
            "setting_21": None,
            "setting_0": False
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
    async def test_incorrect_datatype_storing(self, repository, session_factory):
        class IncorrectDataType:
            pass
        async with session_factory.begin():
            with pytest.raises(ValueError):
                await repository.set_one("incorrect_setting", IncorrectDataType())
        await session_factory.remove()

    @pytest.mark.asyncio
    async def test_set_one_get_one(self, repository, samples, session_factory):
        setting_name = "setting"
        for setting_value in samples.values():
            async with session_factory.begin() as session:
                await repository.set_one(setting_name, setting_value)
                await session.commit()
            async with session_factory.begin():
                result_setting = await repository.get_one(setting_name)
            assert setting_value == result_setting
        await session_factory.remove()

    @pytest.mark.asyncio
    async def test_set_many_get_many(self, repository, samples, session_factory):
        async with session_factory.begin() as session:
            await repository.set_many(samples)
            await session.commit()
        async with session_factory.begin():
            settings_names = list(samples.keys())
            result_settings = await repository.get_many(settings_names)
        assert samples == result_settings
        await session_factory.remove()

    @pytest.mark.asyncio
    async def test_set_all_get_all(self, repository, samples, samples_2, session_factory):
        async with session_factory.begin() as session:
            await repository.set_many(samples_2)
            await session.commit()
        async with session_factory.begin() as session:
            await repository.set_all(samples)
            await session.commit()
        async with session_factory.begin():
            result_settings = await repository.get_all()
            assert samples == result_settings
        await session_factory.remove()
