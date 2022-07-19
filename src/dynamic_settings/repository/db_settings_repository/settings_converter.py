from typing import List, Any, Dict, Iterable

from dynamic_settings.logging import logger
from dynamic_settings.repository.db_settings_repository.dtype_converters import DTypeConverter
from dynamic_settings.repository.db_settings_repository.setting_model import Setting


class SettingsConverter:

    def __init__(self,
                 dtype_converters: List[DTypeConverter]
                 ) -> None:
        self._dtype_converters = dtype_converters.copy()

    def convert_settings_to_python_type(self, settings: Iterable[Setting]) -> Dict[str, Any]:
        converted_settings = {}
        for setting in settings:
            converted_settings[setting.name] = self.convert_one_setting_to_python_type(setting)
        return converted_settings

    def convert_one_setting_to_python_type(self, setting: Setting) -> Any:
        logger.debug(
            f"Converting setting to python type "
            f"{setting.name}: {setting.type} = {setting.value}"
        )

        for converter in self._dtype_converters:
            if converter.TYPE_NAME == setting.type:
                converted_value = converter.to_python_type(setting.value)
                break
        else:
            raise ValueError(f"Converter not found for type {setting.type}")

        return converted_value

    def convert_settings_to_db_format(self, settings: Dict[str, Any]) -> List[Setting]:
        logger.debug("Converting settings to db format")
        converted_settings = []
        for setting_name, setting_value in settings.items():
            converted_setting = self.convert_one_setting_to_db_format(setting_name, setting_value)
            converted_settings.append(converted_setting)
        logger.debug("Settings are converted")
        return converted_settings

    def convert_one_setting_to_db_format(self, setting_name: str, setting_value: Any) -> Setting:
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
            raise ValueError(f"Converter not found for type {type(setting_value)}")

        return setting
