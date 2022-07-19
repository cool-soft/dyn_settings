import pytest

from base_operations_test import SyncBaseRepositoryOperationsTest
from dynamic_settings.repository.dict_settings_repository import DictSettingsRepository


class TestDictSettingsRepositoryBaseOperations(SyncBaseRepositoryOperationsTest):

    @pytest.fixture
    def repository(self):
        return DictSettingsRepository()
