from typing import Any

from sqlalchemy.orm import scoped_session

from dynamic_settings.repository.db_settings_repository.async_db_settings_repository import AsyncDBSettingsRepository
from dynamic_settings.repository.db_settings_repository.sync_db_settings_repository import SyncDBSettingsRepository


def sync_db_settings_provider(db_session_provider: scoped_session,
                              settings_repository: SyncDBSettingsRepository,
                              setting_name: str,
                              remove_session_after_use: bool = True
                              ) -> Any:
    with db_session_provider.begin():
        setting_value = settings_repository.get_one(setting_name)
    if remove_session_after_use:
        db_session_provider.remove()
    return setting_value


async def async_db_settings_provider(db_session_provider: scoped_session,
                                     settings_repository: AsyncDBSettingsRepository,
                                     setting_name: str,
                                     remove_session_after_use: bool = True
                                     ) -> Any:
    async with db_session_provider.begin():
        setting_value = await settings_repository.get_one(setting_name)
    if remove_session_after_use:
        db_session_provider.remove()
    return setting_value
