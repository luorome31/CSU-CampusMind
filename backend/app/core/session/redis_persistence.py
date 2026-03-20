"""
Redis Session 持久化实现

使用 Redis 替代 FileSessionPersistence 提供会话存储。
"""
import json
import time
from abc import ABC, abstractmethod
from typing import Optional
import requests
import redis


class SessionPersistence(ABC):
    """Session 持久化抽象基类"""

    @abstractmethod
    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
        pass

    @abstractmethod
    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        pass

    @abstractmethod
    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        pass


class RedisSessionPersistence(SessionPersistence):
    """
    Redis Session 持久化

    Key 格式: session:{user_id}:{subsystem}
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    def _key(self, user_id: str, subsystem: str) -> str:
        return f"session:{user_id}:{subsystem}"

    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
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
        self._redis.setex(self._key(user_id, subsystem), ttl_seconds, data)

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        data = self._redis.get(self._key(user_id, subsystem))
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

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        if subsystem:
            self._redis.delete(self._key(user_id, subsystem))
        else:
            # 删除用户所有 session
            keys = self._redis.keys(f"session:{user_id}:*")
            if keys:
                self._redis.delete(*keys)