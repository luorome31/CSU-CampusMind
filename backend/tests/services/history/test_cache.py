import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.history.cache import HistoryCacheService


class TestHistoryCacheService:
    """测试 HistoryCacheService"""

    @pytest.fixture
    def mock_redis(self):
        with patch("app.services.history.cache.redis") as mock:
            yield mock

    def test_key_format(self, mock_redis):
        """验证 key 格式"""
        impl = HistoryCacheService.__new__(HistoryCacheService)
        impl._redis = mock_redis
        key = impl._key("dialog123")
        assert key == "history:dialog123"

    def test_invalidate_calls_delete(self, mock_redis):
        """invalidate 应删除 key"""
        impl = HistoryCacheService.__new__(HistoryCacheService)
        impl._redis = mock_redis

        impl.invalidate("dialog123")

        mock_redis.delete.assert_called_once_with("history:dialog123")