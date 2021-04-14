import pytest

from unittests.base_operations_test import BaseRepositoryOperationsTest
from dynamic_settings.repository.simple_settings_repository import SimpleSettingsRepository


class TestSimpleSettingsRepositoryBaseOperations(BaseRepositoryOperationsTest):

    @pytest.fixture
    def repository(self):
        repository = SimpleSettingsRepository()
        return repository
