import pytest


class BaseOperationsTest:

    @pytest.mark.asyncio
    async def test_set_one_get_one(self, repository):
        setting_name = "setting1"
        setting_value = 10

        await repository.set_one(setting_name, setting_value)
        assert setting_value == await repository.get_one(setting_name)