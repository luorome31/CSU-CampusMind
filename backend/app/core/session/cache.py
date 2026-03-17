import time
import threading
from dataclasses import dataclass
from typing import Optional
import requests


@dataclass
class CachedSession:
    """缓存的会话"""
    session: requests.Session
    created_at: float
    last_used: float
    expires_at: float


class SubsystemSessionCache:
    """会话缓存 - 按 用户ID + 子系统 粒度缓存"""

    def __init__(self, ttl_seconds: int = 30 * 60):
        self._ttl = ttl_seconds
        self._cache: dict[str, dict[str, CachedSession]] = {}
        self._lock = threading.Lock()

    def _make_key(self, user_id: str, subsystem: str) -> str:
        return f"{user_id}:{subsystem}"

    def get(self, user_id: str, subsystem: str) -> Optional[CachedSession]:
        with self._lock:
            if user_id not in self._cache or subsystem not in self._cache[user_id]:
                return None

            cached = self._cache[user_id][subsystem]
            now = time.time()

            if now > cached.expires_at:
                del self._cache[user_id][subsystem]
                if not self._cache[user_id]:
                    del self._cache[user_id]
                return None

            cached.last_used = now
            return cached

    def set(self, user_id: str, subsystem: str, session: requests.Session) -> None:
        with self._lock:
            now = time.time()
            if user_id not in self._cache:
                self._cache[user_id] = {}

            self._cache[user_id][subsystem] = CachedSession(
                session=session,
                created_at=now,
                last_used=now,
                expires_at=now + self._ttl
            )

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        with self._lock:
            if user_id not in self._cache:
                return
            if subsystem is None:
                del self._cache[user_id]
            elif subsystem in self._cache[user_id]:
                del self._cache[user_id][subsystem]
