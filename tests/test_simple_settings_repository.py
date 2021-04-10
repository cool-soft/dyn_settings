import unittest

from dynamic_settings.repository.simple_async_settings_repository import SimpleAsyncSettingsRepository


class ExecuteBaseOperations(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self._repository = SimpleAsyncSettingsRepository()

    async def test_set_one_get_one(self):
        setting_name = "setting1"
        setting_value = 10

        await self._repository.set_one(setting_name, setting_value)
        self.assertEqual(setting_value, await self._repository.get_one(setting_name))

    async def test_set_many_get_many(self):
        settings = {
            "a": 10,
            "b": "b"
        }

        await self._repository.set_many(settings)
        settings_names = list(settings.keys())
        result_settings = await self._repository.get_many(settings_names)
        self.assertDictEqual(settings, result_settings)

    async def test_set_all_get_all(self):
        settings = {
            "a": 10,
            "b": "b"
        }

        await self._repository.set_all(settings)
        result_settings = await self._repository.get_all()
        self.assertDictEqual(settings, result_settings)


if __name__ == '__main__':
    unittest.main()
