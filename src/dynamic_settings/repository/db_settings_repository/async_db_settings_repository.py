from typing import Any, Dict, List, Callable, Iterator

from sqlalchemy.future import select

from dynamic_settings.logging import logger
from .setting_model import Setting
from .settings_converter import SettingsConverter
from ..abstract_settings_repository import AbstractAsyncSettingsRepository


class AsyncDBSettingsRepository(AbstractAsyncSettingsRepository):

    def __init__(self,
                 session_provider: Callable,
                 dtype_converter: SettingsConverter,
                 a=1
                 ) -> None:
        self._db_session_provider = session_provider
        self._dtype_converter = dtype_converter
        logger.debug(f"Creating instance. session_factory: {session_provider}.")

    async def get_one(self, setting_name: str) -> Any:
        logger.debug(f"Requested setting {setting_name}")
        session = self._db_session_provider()
        statement = select(Setting).where(Setting.name == setting_name)
        setting: Setting = (await session.execute(statement)).scalars().one()
        converted_setting = self._dtype_converter.convert_one_setting_to_python_type(setting)
        return converted_setting

    async def set_one(self, setting_name: str, setting_value: Any) -> None:
        logger.debug(f"Setting {setting_name} is set to {setting_value}")
        converted_setting = self._dtype_converter.convert_one_setting_to_db_format(setting_name, setting_value)
        session = self._db_session_provider()
        await session.merge(converted_setting)

    async def get_many(self, setting_names: List[str]) -> Dict[str, Any]:
        logger.debug(f"Requested settings: {setting_names}")
        session = self._db_session_provider()
        statement = select(Setting).where(Setting.name.in_(setting_names))
        settings: Iterator[Setting] = (await session.execute(statement)).scalars().all()
        converted_settings = self._dtype_converter.convert_settings_to_python_type(settings)
        return converted_settings

    async def set_many(self, settings: Dict[str, Any]) -> None:
        logger.debug("Set many settings is requested")
        converted_settings = self._dtype_converter.convert_settings_to_db_format(settings)
        session = self._db_session_provider()
        for setting in converted_settings:
            await session.merge(setting)

    async def get_all(self) -> Dict[str, Any]:
        logger.debug("All settings are requested")
        session = self._db_session_provider()
        statement = select(Setting)
        settings: Iterator[Setting] = (await session.execute(statement)).scalars().all()
        converted_settings = self._dtype_converter.convert_settings_to_python_type(settings)
        return converted_settings

    async def set_all(self, settings: Dict[str, Any]) -> None:
        logger.debug("Set all settings is requested")
        session = self._db_session_provider()
        setting_names = list(settings.keys())
        statement = select(Setting).where(Setting.name.not_in(setting_names))
        selected_settings = (await session.execute(statement)).scalars().all()
        for selected_setting in selected_settings:
            await session.delete(selected_setting)
        converted_settings = self._dtype_converter.convert_settings_to_db_format(settings)
        for setting in converted_settings:
            await session.merge(setting)
