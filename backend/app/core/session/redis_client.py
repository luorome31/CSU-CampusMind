"""
Global Redis Client Singleton

Manages Redis connection pool lifecycle via FastAPI lifespan.
Uses redis.asyncio for full async support.
"""
import logging
from typing import Optional
from redis.asyncio import Redis, ConnectionPool

logger = logging.getLogger(__name__)

_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


async def init_redis(redis_url: str) -> Redis:
    """Initialize global Redis connection pool on startup."""
    global _redis_pool, _redis_client
    _redis_pool = ConnectionPool.from_url(redis_url, decode_responses=True)
    _redis_client = Redis(connection_pool=_redis_pool)
    # Test connection
    await _redis_client.ping()
    logger.info(f"[REDIS] Connection pool initialized: {redis_url}")
    return _redis_client


async def close_redis():
    """Close Redis connection pool on shutdown."""
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.aclose()
        logger.info("[REDIS] Client closed")
    if _redis_pool:
        await _redis_pool.disconnect()
        logger.info("[REDIS] Pool disconnected")
    _redis_client = None
    _redis_pool = None


def get_redis() -> Redis:
    """Get global Redis client (raises if not initialized)."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


def is_redis_initialized() -> bool:
    """Check if Redis client is initialized."""
    return _redis_client is not None
