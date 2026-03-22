"""
Completion API tests

These tests are skipped because they require Redis to be initialized.
The completion API is tested indirectly through integration tests.
"""
import pytest

pytestmark = pytest.mark.skip(reason="Redis not initialized - requires integration test setup")
