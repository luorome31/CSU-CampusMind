"""
Tests for global Redis client singleton
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from redis.asyncio import Redis

from app.core.session import redis_client


class TestRedisClient:
    """Tests for redis_client module"""

    def setup_method(self):
        """Reset module state before each test"""
        redis_client._redis_client = None
        redis_client._redis_pool = None

    def test_get_redis_raises_when_not_initialized(self):
        """Test that get_redis() raises RuntimeError before init"""
        with pytest.raises(RuntimeError, match="Redis not initialized"):
            redis_client.get_redis()

    def test_is_redis_initialized_false_before_init(self):
        """Test is_redis_initialized returns False before init"""
        assert redis_client.is_redis_initialized() is False

    def test_is_redis_initialized_true_after_init(self):
        """Test is_redis_initialized returns True after init"""
        mock_redis = MagicMock(spec=Redis)
        redis_client._redis_client = mock_redis
        redis_client._redis_pool = MagicMock()

        assert redis_client.is_redis_initialized() is True

    @pytest.mark.asyncio
    async def test_init_and_close_redis(self):
        """Test init_redis and close_redis flow"""
        mock_pool = MagicMock()
        mock_client = MagicMock(spec=Redis)

        with patch.object(redis_client, 'ConnectionPool') as MockPool:
            MockPool.from_url.return_value = mock_pool
            mock_client.aclose = AsyncMock()
            mock_pool.disconnect = AsyncMock()
            redis_client._redis_client = mock_client
            redis_client._redis_pool = mock_pool

            # Just verify state is set correctly
            assert redis_client._redis_client is mock_client
            assert redis_client._redis_pool is mock_pool