from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dynamic_settings.repository.db_settings_repository.setting_model import Setting
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository
from dynamic_settings.repository.db_settings_repository import dtype_converters
from dynamic_settings.repository.db_settings_repository.settings_converter import SettingsConverter


class TestSyncDBSettingsRepositoryBaseOperations:

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

    def test_incorrect_datatype_storing(self, repository, session_factory):
        class IncorrectDataType:
            pass
        with session_factory.begin():
            with pytest.raises(ValueError):
                repository.set_one("incorrect_setting", IncorrectDataType())
        session_factory.remove()

    def test_set_one_get_one(self, repository, samples, session_factory):
        setting_name = "setting"
        with session_factory.begin():
            for setting_value in samples.values():
                repository.set_one(setting_name, setting_value)
                result_setting = repository.get_one(setting_name)
                assert setting_value == result_setting
        session_factory.remove()

    def test_set_many_get_many(self, repository, samples, session_factory):
        with session_factory.begin():
            repository.set_many(samples)
            settings_names = list(samples.keys())
            result_settings = repository.get_many(settings_names)
        assert samples == result_settings
        session_factory.remove()

    def test_set_all_get_all(self, repository, samples, samples_2, session_factory):
        with session_factory.begin():
            repository.set_many(samples_2)
            repository.set_all(samples)
            result_settings = repository.get_all()
            assert samples == result_settings
        session_factory.remove()
