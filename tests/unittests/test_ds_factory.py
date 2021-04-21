import pytest
from dynamic_settings.service.async_settings_service import AsyncSettingsService

from dynamic_settings.factory.async_factory import AsyncFactory
from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository


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
    def settings_names(self, settings):
        return list(settings.keys())

    @pytest.fixture
    def settings_service(self, repository):
        return AsyncSettingsService(settings_repository=repository)

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
    def factory(self, class_, settings_service, args, kwargs, settings_names):
        return AsyncFactory(
            class_=class_,
            settings_service=settings_service,
            settings_names=settings_names,
            args=args,
            kwargs=kwargs
        )

    @pytest.mark.asyncio
    async def test_creating_instance(self, factory, settings_service, args, kwargs, settings):
        await settings_service.set_settings(settings)

        instance = await factory.create_instance()

        settings_with_kwargs = settings.copy()
        settings_with_kwargs.update(kwargs)

        assert instance.args == tuple(args)
        assert instance.kwargs == settings_with_kwargs
