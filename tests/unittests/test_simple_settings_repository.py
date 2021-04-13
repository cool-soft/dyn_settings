import pytest

from unittests.base_operations_test import BaseRepositoryOperationsTest
from dynamic_settings.repository.simple_async_settings_repository import SimpleAsyncSettingsRepository


class TestSimpleSettingsRepositoryBaseOperations(BaseRepositoryOperationsTest):

    @pytest.fixture
    def repository(self):
        repository = SimpleAsyncSettingsRepository()
        return repository
