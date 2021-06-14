from datetime import datetime, timedelta

import pytest


class BaseRepositoryOperationsTest:

    @pytest.mark.asyncio
    async def test_set_one_get_one(self, repository):
        setting_name = "setting"
        values = [None, True, False, 10, 50.23, "string value", datetime.now(), timedelta(seconds=123.45)]

        for setting_value in values:
            await repository.set_one(setting_name, setting_value)

            result_setting = await repository.get_one(setting_name)
            assert setting_value == result_setting

    @pytest.mark.asyncio
    async def test_set_many_get_many(self, repository):
        settings = {
            "setting_0": None,
            "setting_1": True,
            "setting_2": False,
            "setting_3": 10,
            "setting_4": 50.23,
            "setting_5": "string value",
            "setting_6": datetime.now(),
            "setting_7": timedelta(seconds=123.45)
        }

        await repository.set_many(settings)

        settings_names = list(settings.keys())
        result_settings = await repository.get_many(settings_names)
        assert settings == result_settings

    @pytest.mark.asyncio
    async def test_set_all_get_all(self, repository):
        fake_setting = {
            "setting_20": 1,
            "setting_21": None,
            "setting_0": False
        }

        settings = {
            "setting_0": None,
            "setting_1": True,
            "setting_2": False,
            "setting_3": 10,
            "setting_4": 50.23,
            "setting_5": "string value",
            "setting_6": datetime.now(),
            "setting_7": timedelta(seconds=123.45)
        }

        await repository.set_many(fake_setting)
        await repository.set_all(settings)

        result_settings = await repository.get_all()
        assert settings == result_settings
