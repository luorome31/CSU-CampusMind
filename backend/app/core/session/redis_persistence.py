"""
Redis Session 持久化实现

使用 Redis 替代 FileSessionPersistence 提供会话存储。
使用全局 Redis 连接池单例。
"""
import json
import time
from typing import Optional
import requests
from redis.asyncio import Redis

from app.api.dependencies import get_redis_client
from .persistence import SessionPersistence


class RedisSessionPersistence(SessionPersistence):
    """
    Redis Session 持久化

    Key 格式: session:{user_id}:{subsystem}
    """

    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis

    def _key(self, user_id: str, subsystem: str) -> str:
        return f"session:{user_id}:{subsystem}"

    async def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = {
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
            }

        data = json.dumps({
            "cookies": cookies_dict,
            "saved_at": time.time()
        })
        await self._redis.setex(self._key(user_id, subsystem), ttl_seconds, data)

    async def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        data = await self._redis.get(self._key(user_id, subsystem))
        if not data:
            return None

        session = requests.Session()
        cookies_dict = json.loads(data).get("cookies", {})

        for name, info in cookies_dict.items():
            session.cookies.set(
                name,
                info["value"],
                domain=info.get("domain"),
                path=info.get("path", "/"),
                secure=info.get("secure", False),
            )

        return session

    async def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        if subsystem:
            await self._redis.delete(self._key(user_id, subsystem))
        else:
            # 删除用户所有 session
            keys = []
            async for key in self._redis.scan_iter(f"session:{user_id}:*"):
                keys.append(key)
            if keys:
                await self._redis.delete(*keys)