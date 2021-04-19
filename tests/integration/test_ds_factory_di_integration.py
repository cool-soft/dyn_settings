import pytest
from aiorwlock import RWLock
from dependency_injector import containers
from dependency_injector.providers import Singleton, Object, Dependency, Container

from dynamic_settings.ds_service.async_dynamic_settings_service import AsyncDynamicSettingsService
from dynamic_settings.dynamic_settings_factory import DSFactory
from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository


class PublicArgsKWArgsStructure:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class FactoryUser:

    def __init__(self, factory: DSFactory):
        self.factory = factory
        self.instance = None

    async def request_instance(self):
        self.instance = await self.factory.create_instance()


class FactoryContainer(containers.DeclarativeContainer):
    args = Dependency()
    kwargs = Dependency()
    setting_names = Dependency()

    settings_repository = Dependency()
    settings_rwlock = Dependency()

    factory = Singleton(
        DSFactory,
        class_=Object(PublicArgsKWArgsStructure),
        settings_repository=settings_repository,
        settings_rwlock=settings_rwlock,
        args=args,
        kwargs=kwargs,
        settings_names=setting_names
    )


class DynamicSettingsContainer(containers.DeclarativeContainer):

    settings_repository = Dependency()
    settings_rwlock = Dependency()
    default_settings = Object(None)

    settings_service = Singleton(AsyncDynamicSettingsService,
                                 settings_repository=settings_repository,
                                 settings_rwlock=settings_rwlock,
                                 defaults=default_settings)


class FactoryUserContainer(containers.DeclarativeContainer):

    factory = Dependency()
    factory_user = Singleton(FactoryUser,
                             factory=factory)


class ApplicationContainer(containers.DeclarativeContainer):
    settings_repository = Singleton(SimpleSettingsRepository)
    settings_rwlock = Singleton(RWLock)

    settings_pkg = Container(DynamicSettingsContainer,
                             settings_repository=settings_repository,
                             settings_rwlock=settings_rwlock)

    factory_pkg = Container(FactoryContainer,
                            settings_repository=settings_repository,
                            settings_rwlock=settings_rwlock)

    factory_user_pkg = Container(FactoryUserContainer,
                                 factory=factory_pkg.factory)


class TestDSFactoryDIIntegration:

    @pytest.fixture
    def settings(self):
        return {
            "setting_0": 0,
            "setting_1": "abc"
        }

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
    async def application_container(self, args, kwargs, settings):
        app_pkg = ApplicationContainer()

        app_pkg.factory_pkg.args.override(Object(args))
        app_pkg.factory_pkg.kwargs.override(Object(kwargs))
        app_pkg.factory_pkg.setting_names.override(Object(list(settings.keys())))

        settings_service = app_pkg.settings_pkg.settings_service()
        await settings_service.initialize_repository()
        await settings_service.set_settings(settings)

        return app_pkg

    @pytest.fixture
    async def factory_user(self, application_container):
        # noinspection PyUnresolvedReferences
        user = application_container.factory_user_pkg.factory_user()
        return user

    @pytest.mark.asyncio
    async def test_creating_instance(self, factory_user, args, kwargs, settings):
        # noinspection PyUnresolvedReferences
        await factory_user.request_instance()
        # noinspection PyUnresolvedReferences
        instance = factory_user.instance

        settings_with_kwargs = settings.copy()
        settings_with_kwargs.update(kwargs)

        assert instance.args == tuple(args)
        assert instance.kwargs == settings_with_kwargs
