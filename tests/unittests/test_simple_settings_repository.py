import pytest

from unittests.base_operations_test import BaseRepositoryOperationsTest
from dynamic_settings.repository.dict_settings_repository import DictSettingsRepository


class TestSimpleSettingsRepositoryBaseOperations(BaseRepositoryOperationsTest):

    @pytest.fixture
    def repository(self):
        return DictSettingsRepository()
