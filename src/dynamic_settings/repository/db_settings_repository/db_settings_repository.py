from typing import Any, Dict, List, Callable, Iterator

from dynamic_settings.logger import logger
from sqlalchemy.future import select

from .dtype_converters import DTypeConverter
from .setting_model import Setting
from ..abstract_settings_repository import AbstractSettingsRepository


class DBSettingsRepository(AbstractSettingsRepository):

    def __init__(self,
                 session_factory: Callable,
                 dtype_converters: List[DTypeConverter]
                 ) -> None:

        self._db_session_factory = session_factory
        self._dtype_converters = dtype_converters.copy()

        logger.debug(
            f"Creating instance:"
            f"session_factory: {session_factory}; "
            f"converters count: {len(dtype_converters)}"
        )

    async def get_one(self, setting_name: str) -> Any:
        logger.debug(f"Requested setting {setting_name}")

        async with self._db_session_factory() as session:
            statement = select(Setting).filter(Setting.name == setting_name)
            setting: Setting = (await session.execute(statement)).scalars().one()

        converted_setting = self._convert_one_setting_to_python_type(setting)
        return converted_setting

    async def set_one(self, setting_name: str, setting_value: Any) -> None:
        logger.debug(f"Setting {setting_name} is set to {setting_value}")

        converted_setting = self._convert_one_setting_to_db_format(setting_name, setting_value)
        async with self._db_session_factory() as session:
            await session.merge(converted_setting)
            await session.commit()

    async def get_many(self, setting_names: List[str]) -> Dict[str, Any]:
        logger.debug(f"Requested settings: {setting_names}")

        async with self._db_session_factory() as session:
            statement = select(Setting).filter(Setting.name.in_(setting_names))
            settings: Iterator[Setting] = (await session.execute(statement)).scalars().all()

        converted_settings = self._convert_settings_to_python_types(settings)
        return converted_settings

    async def set_many(self, settings: Dict[str, Any]) -> None:
        logger.debug("Set many settings is requested")

        converted_settings = self._convert_settings_to_db_format(settings)
        async with self._db_session_factory() as session:
            for setting in converted_settings:
                await session.merge(setting)
            await session.commit()

    async def get_all(self) -> Dict[str, Any]:
        logger.debug("All settings are requested")

        async with self._db_session_factory() as session:
            statement = select(Setting)
            settings: Iterator[Setting] = (await session.execute(statement)).scalars().all()

        converted_settings = self._convert_settings_to_python_types(settings)
        return converted_settings

    async def set_all(self, settings: Dict[str, Any]) -> None:
        logger.debug("Set all settings is requested")

        async with self._db_session_factory() as session:
            setting_names = list(settings.keys())
            statement = select(Setting).filter(Setting.name.not_in(setting_names))
            selected_settings = (await session.execute(statement)).scalars().all()
            for selected_setting in selected_settings:
                await session.delete(selected_setting)
            converted_settings = self._convert_settings_to_db_format(settings)
            for setting in converted_settings:
                await session.merge(setting)
            await session.commit()

    def _convert_settings_to_python_types(self, settings: Iterator[Setting]):
        logger.debug("Converting settings to python type")

        converted_settings = {}
        for setting in settings:
            converted_setting_value = self._convert_one_setting_to_python_type(setting)
            converted_settings[setting.name] = converted_setting_value

        logger.debug("Settings are converted")
        return converted_settings

    def _convert_one_setting_to_python_type(self, setting: Setting) -> Any:
        logger.debug(
            f"Converting setting to python type "
            f"{setting.name}: {setting.type} = {setting.value}"
        )

        for converter in self._dtype_converters:
            if converter.TYPE_NAME == setting.type:
                converted_value = converter.to_python_type(setting.value)
                break
        else:
            raise RuntimeError(f"Converter not found for type {setting.type}")

        return converted_value

    def _convert_settings_to_db_format(self, settings: Dict[str, Any]) -> List[Setting]:
        logger.debug("Converting settings to db format")

        converted_settings = []
        for setting_name, setting_value in settings.items():
            converted_setting = self._convert_one_setting_to_db_format(setting_name, setting_value)
            converted_settings.append(converted_setting)

        logger.debug("Settings are converted")
        return converted_settings

    def _convert_one_setting_to_db_format(self, setting_name: str, setting_value: Any) -> Setting:
        logger.debug(
            f"Converting setting to db format "
            f"{setting_name}: {type(setting_value)} = {setting_value}"
        )

        for converter in self._dtype_converters:
            if isinstance(setting_value, converter.PYTHON_TYPE):
                converted_value = converter.to_db_format(setting_value)
                setting = Setting(name=setting_name, type=converter.TYPE_NAME, value=converted_value)
                break
        else:
            raise RuntimeError(f"Converter not found for type {type(setting_value)}")

        return setting
