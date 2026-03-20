import os
import json
import time
import threading
from abc import ABC, abstractmethod
from typing import Optional
import requests


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


class FileSessionPersistence(SessionPersistence):
    """
    [DEPRECATED] 文件存储 Session 持久化

    请使用 RedisSessionPersistence 替代。
    计划移除时间: 2026-06-01
    """

    def __init__(self, storage_path: str = "./data/csu_sessions.json"):
        self._storage_path = storage_path
        self._lock = threading.Lock()

        # 确保目录存在
        os.makedirs(os.path.dirname(storage_path) or ".", exist_ok=True)

    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
        with self._lock:
            data = self._load_all()

            cookies_dict = {}
            for cookie in session.cookies:
                cookies_dict[cookie.name] = {
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "expires": cookie.expires,
                }

            if user_id not in data:
                data[user_id] = {}

            data[user_id][subsystem] = {
                "cookies": cookies_dict,
                "saved_at": time.time(),
                "expires_at": time.time() + ttl_seconds,
            }

            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        with self._lock:
            data = self._load_all()

            if user_id not in data or subsystem not in data[user_id]:
                return None

            session_data = data[user_id][subsystem]

            if time.time() > session_data.get("expires_at", 0):
                return None

            session = requests.Session()
            cookies_dict = session_data.get("cookies", {})

            for name, cookie_info in cookies_dict.items():
                session.cookies.set(
                    name,
                    cookie_info["value"],
                    domain=cookie_info.get("domain"),
                    path=cookie_info.get("path", "/"),
                    secure=cookie_info.get("secure", False),
                )

            return session

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        with self._lock:
            data = self._load_all()
            if subsystem:
                if user_id in data and subsystem in data[user_id]:
                    del data[user_id][subsystem]
            else:
                if user_id in data:
                    del data[user_id]

            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)

    def _load_all(self) -> dict:
        if not os.path.exists(self._storage_path):
            return {}
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}


# TODO: 预留 Redis 实现
# class RedisSessionPersistence(SessionPersistence):
#     def __init__(self, redis_url: str):
#         ...
