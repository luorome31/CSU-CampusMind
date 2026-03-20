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
        # Create mocks
        mock_pool = MagicMock()
        mock_pool.disconnect = AsyncMock()

        # Create a mock Redis client with async methods
        mock_client = MagicMock()
        mock_client.ping = AsyncMock()
        mock_client.aclose = AsyncMock()

        with patch.object(redis_client, 'ConnectionPool') as MockPool:
            with patch.object(redis_client, 'Redis') as MockRedis:
                MockPool.from_url.return_value = mock_pool
                MockRedis.return_value = mock_client

                # Call init_redis
                await redis_client.init_redis("redis://localhost:6379/0")

                # Verify ConnectionPool.from_url was called
                MockPool.from_url.assert_called_once_with("redis://localhost:6379/0", decode_responses=True)

                # Verify Redis was instantiated with the pool
                MockRedis.assert_called_once_with(connection_pool=mock_pool)

                # Verify ping was called
                mock_client.ping.assert_called_once()

                # Verify globals are set
                assert redis_client._redis_client is mock_client
                assert redis_client._redis_pool is mock_pool

                # Call close_redis
                await redis_client.close_redis()

                # Verify cleanup methods were called
                mock_client.aclose.assert_called_once()
                mock_pool.disconnect.assert_called_once()

                # Verify globals are cleared
                assert redis_client._redis_client is None
                assert redis_client._redis_pool is None