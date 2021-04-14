import pytest

from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository
from dynamic_settings.dynamic_settings_factory import DSFactory


class TestDSFactory:

    @pytest.fixture
    def repository(self):
        repository = SimpleSettingsRepository()
        return repository

    @pytest.fixture
    def settings(self):
        return {
            "setting_0": 0,
            "setting_1": "abc"
        }

    @pytest.fixture
    async def repository_with_settings(self, repository, settings):
        await repository.set_many(settings)
        return repository

    @pytest.fixture
    def args(self):
        return [1, None, True]

    @pytest.fixture
    def kwargs(self):
        return {
            "setting_2": False,
            "setting_3": None
        }

    @pytest.fixture
    def class_(self):
        class SomeClass:

            def __init__(self, *args, **kwargs):
                self.args = args
                self.kwargs = kwargs

        return SomeClass

    @pytest.fixture
    def setting_names(self, settings):
        return list(settings.keys())

    @pytest.fixture
    def factory(self, class_, repository_with_settings, args, kwargs, setting_names):
        # noinspection PyTypeChecker
        return DSFactory(
            class_=class_,
            settings_repository=repository_with_settings,
            args=args,
            kwargs=kwargs,
            settings_names=setting_names
        )

    @pytest.mark.asyncio
    async def test_creating_instance(self, factory, args, kwargs, settings):
        instance = await factory.create_instance()

        settings_with_kwargs = settings.copy()
        settings_with_kwargs.update(kwargs)

        assert instance.args == tuple(args)
        assert instance.kwargs == settings_with_kwargs
