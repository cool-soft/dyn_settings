from typing import Any

from dynamic_settings.repository.abstract_settings_repository import AbstractSettingsRepository


async def get_one_setting(settings_repository: AbstractSettingsRepository, setting_name: str) -> Any:
    return await settings_repository.get_one(setting_name)
