import pytest

from unittests.base_operations_test import BaseOperationsTest
from dynamic_settings.repository.simple_async_settings_repository import SimpleAsyncSettingsRepository


class TestSimpleSettingsRepositoryBaseOperations(BaseOperationsTest):

    @pytest.fixture
    def repository(self):
        repository = SimpleAsyncSettingsRepository()
        return repository
