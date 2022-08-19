from datetime import datetime, timedelta

import pytest
from dynamic_settings.repository.di_integration import sync_db_settings_provider
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository


class TestSyncSettingsDBDIIntegration:

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

    db_url = "sqlite:///:memory:"

    @pytest.fixture
    def session_factory(self):
        engine = create_engine(self.db_url)
        with engine.begin() as conn:
            Setting.metadata.drop_all(conn)
            Setting.metadata.create_all(conn)
        db_session_maker = sessionmaker(
            expire_on_commit=False,
            bind=engine
        )
        session_factory = scoped_session(
            db_session_maker
        )
        return session_factory

    @pytest.fixture
    def repository(self, session_factory, converters):
        return SyncDBSettingsRepository(session_factory, SettingsConverter(converters))

    def test_di_integrator(self, session_factory, repository, samples):
        with session_factory.begin() as session:
            repository.set_many(samples)
            session.commit()
        for setting_name, setting_value in samples.items():
            assert setting_value == sync_db_settings_provider(
                session_factory,
                repository,
                setting_name,
                remove_session_after_use=False
            )
        session_factory.remove()
