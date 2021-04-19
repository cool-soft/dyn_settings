import logging
from typing import List, Optional, Any, Dict

from aiorwlock import RWLock

from dynamic_settings.repository.settings_repository import SettingsRepository


class DSFactory:

    def __init__(self,
                 class_: Optional = None,
                 settings_repository: Optional[SettingsRepository] = None,
                 settings_rwlock: Optional[RWLock] = None,
                 settings_names: Optional[List[str]] = None,
                 args: Optional[List[Any]] = None,
                 kwargs: Optional[Dict[str, Any]] = None) -> None:

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug("Creating instance")

        self._class = class_
        self._settings_repository = settings_repository
        self._settings_rwlock = settings_rwlock
        self._settings_names = settings_names

        if args is None:
            args = []
        self._args = args
        if kwargs is None:
            kwargs = {}
        self._kwargs = kwargs

        self._logger.debug(f"Class: {self._class.__name__}")

    def set_class(self, class_) -> None:
        self._logger.debug(f"Class is set to {class_.__name__}")
        self._class = class_

    def set_settings_repository(self, repository: SettingsRepository) -> None:
        self._logger.debug(f"Settings repository is set to {repository.__class__.__name__}")
        self._settings_repository = repository

    def set_settings_names(self, settings_names: List[str]) -> None:
        self._logger.debug(f"Settings names are set to {settings_names}")
        self._settings_names = settings_names

    def set_settings_rwlock(self, lock: RWLock) -> None:
        self._logger.debug(f"Settings rwlock is set to {lock}")
        self._settings_rwlock = lock

    def set_args(self, args: List[Any]) -> None:
        self._logger.debug(f"Args are set to {args}")
        self._args = args

    def set_kwargs(self, kwargs: Dict[str, Any]) -> None:
        self._logger.debug(f"Keyword args are set to {kwargs}")
        self._kwargs = kwargs

    async def __call__(self):
        return await self.create_instance()

    async def create_instance(self) -> Any:
        self._logger.debug(f"Creating instance of {self._class.__name__}")

        args = self._args.copy()
        kwargs = self._kwargs.copy()

        async with self._settings_rwlock.reader_lock:
            dynamic_settings = await self._settings_repository.get_many(self._settings_names)
        kwargs.update(dynamic_settings)

        instance = self._class(*args, **kwargs)
        self._logger.debug(f"Instance of {self._class.__name__} is created")
        return instance
