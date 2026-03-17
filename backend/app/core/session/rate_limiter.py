import time
import threading
from typing import Dict, List


class LoginRateLimiter:
    """登录频率控制器 - 防止账号被封"""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def can_login(self, user_id: str) -> bool:
        with self._lock:
            now = time.time()
            if user_id in self._attempts:
                self._attempts[user_id] = [
                    t for t in self._attempts[user_id]
                    if now - t < self._window_seconds
                ]
            count = len(self._attempts.get(user_id, []))
            return count < self._max_attempts

    def record_login(self, user_id: str) -> None:
        with self._lock:
            if user_id not in self._attempts:
                self._attempts[user_id] = []
            self._attempts[user_id].append(time.time())

    def get_wait_time(self, user_id: str) -> float:
        with self._lock:
            if user_id not in self._attempts:
                return 0.0
            now = time.time()
            recent = [t for t in self._attempts[user_id] if now - t < self._window_seconds]
            if len(recent) < self._max_attempts:
                return 0.0
            oldest = min(recent)
            return self._window_seconds - (now - oldest)
