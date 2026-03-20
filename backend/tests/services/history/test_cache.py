"""
Tests for HistoryCacheService
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from dataclasses import dataclass

from app.services.history.cache import HistoryCacheService


@dataclass
class MockChatHistory:
    """Mock ChatHistory with to_dict method"""
    id: str
    dialog_id: str
    role: str
    content: str
    created_at: str = "2024-01-01T00:00:00"

    def to_dict(self):
        return {
            "id": self.id,
            "dialog_id": self.dialog_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }


class TestHistoryCacheService:
    """Tests for HistoryCacheService"""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock async Redis client"""
        mock = AsyncMock()
        return mock

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create HistoryCacheService with mock Redis"""
        return HistoryCacheService(redis=mock_redis)

    def test_key_format(self, cache_service):
        """Test cache key format"""
        assert cache_service._key("dialog123") == "history:dialog123"

    @pytest.mark.asyncio
    async def test_get_history_cache_hit(self, cache_service, mock_redis):
        """Test get_history returns cached data"""
        cached_data = '[{"id": "1", "role": "user", "content": "hello"}]'
        mock_redis.get = AsyncMock(return_value=cached_data)

        result = await cache_service.get_history("dialog123")

        assert result is not None
        assert len(result) == 1
        assert result[0]["content"] == "hello"
        mock_redis.get.assert_called_once_with("history:dialog123")

    @pytest.mark.asyncio
    async def test_update_cache(self, cache_service, mock_redis):
        """Test update_cache writes to Redis"""
        mock_redis.setex = AsyncMock()
        histories = [
            MockChatHistory(id="1", dialog_id="d1", role="user", content="hi")
        ]

        await cache_service.update_cache("dialog123", histories)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "history:dialog123"
        assert call_args[0][1] == 3600  # TTL

    @pytest.mark.asyncio
    async def test_invalidate(self, cache_service, mock_redis):
        """Test invalidate deletes cache key"""
        mock_redis.delete = AsyncMock()

        await cache_service.invalidate("dialog123")

        mock_redis.delete.assert_called_once_with("history:dialog123")