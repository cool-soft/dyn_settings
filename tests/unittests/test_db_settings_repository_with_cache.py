import pytest

from dynamic_settings.repository.db_settings_repository import DBSettingsRepositoryWithCache
from unittests.test_db_settings_repository import TestDBSettingsRepositoryBaseOperations \
    as DBSettingRepositoryBaseOperationsTest


class TestDBSettingsRepositoryWithCacheBaseOperations(DBSettingRepositoryBaseOperationsTest):

    @pytest.fixture
    def repository(self, db_session_factory, converters):
        repository = DBSettingsRepositoryWithCache()
        repository.set_db_session_factory(db_session_factory)
        repository.set_dtype_converters(converters)
        return repository
