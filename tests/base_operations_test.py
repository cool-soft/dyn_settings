from datetime import datetime, timedelta

import pytest


# noinspection PyMethodMayBeStatic
class SyncBaseRepositoryOperationsTest:

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

    def test_set_one_get_one(self, repository, samples):
        setting_name = "setting"
        for setting_value in samples.values():
            repository.set_one(setting_name, setting_value)
            result_setting = repository.get_one(setting_name)
            assert setting_value == result_setting

    def test_set_many_get_many(self, repository, samples):
        repository.set_many(samples)
        settings_names = list(samples.keys())
        result_settings = repository.get_many(settings_names)
        assert samples == result_settings

    def test_set_all_get_all(self, repository, samples, samples_2):
        repository.set_many(samples_2)
        repository.set_all(samples)
        result_settings = repository.get_all()
        assert samples == result_settings
