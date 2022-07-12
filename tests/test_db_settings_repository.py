import pytest
import pytest_asyncio
from sqlalchemy import orm
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from dynamic_settings.repository.db_settings_repository import DBSettingsRepository
from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from base_operations_test import BaseRepositoryOperationsTest


class TestDBSettingsRepositoryBaseOperations(BaseRepositoryOperationsTest):

    db_url = "sqlite+aiosqlite:///:memory:"

    @pytest_asyncio.fixture
    async def db(self):
        db_engine = create_async_engine(self.db_url)
        async with db_engine.begin() as conn:
            await conn.run_sync(Setting.metadata.drop_all)
            await conn.run_sync(Setting.metadata.create_all)
        return db_engine

    @pytest.fixture
    def db_session_factory(self, db):
        session_factory = orm.scoped_session(
            orm.sessionmaker(autocommit=False,
                             autoflush=False,
                             bind=db,
                             class_=AsyncSession),
        )
        return session_factory

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

    @pytest.fixture
    def repository(self, db_session_factory, converters):
        return DBSettingsRepository(db_session_factory, converters)

    @pytest.mark.asyncio
    async def test_incorrect_datatype_storing(self, repository):
        class IncorrectDataType:
            pass

        with pytest.raises(ValueError):
            await repository.set_one("incorrect_setting", IncorrectDataType())
