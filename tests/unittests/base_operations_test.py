import pytest


class BaseRepositoryOperationsTest:

    @pytest.mark.asyncio
    async def test_set_one_get_one(self, repository):
        setting_name = "setting1"
        setting_value = 10

        await repository.set_one(setting_name, setting_value)
        assert setting_value == await repository.get_one(setting_name)

    @pytest.mark.asyncio
    async def test_set_many_get_many(self, repository):
        settings = {
            "a": 10,
            "b": "b"
        }

        await repository.set_many(settings)
        settings_names = list(settings.keys())
        result_settings = await repository.get_many(settings_names)
        assert settings == result_settings

    @pytest.mark.asyncio
    async def test_set_all_get_all(self, repository):
        settings = {
            "a": 10,
            "b": "b"
        }

        await repository.set_all(settings)
        result_settings = await repository.get_all()
        assert settings == result_settings
