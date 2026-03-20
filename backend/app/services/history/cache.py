"""
对话历史缓存服务

使用 Redis LRU 缓存对话历史，减少数据库 IO。
Write-through 策略：写入时同时更新缓存。
"""
import json
from typing import List, Optional

from fastapi import Depends
from redis.asyncio import Redis

from app.config import settings
from app.api.dependencies import get_redis_client


class HistoryCacheService:
    """
    对话历史缓存服务 (Redis LRU)

    先查缓存，未命中查 DB，然后写入缓存。
    写入时使用 write-through 策略：保存 DB 后同时更新缓存。
    """

    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis
        self._ttl = 3600  # 1小时

    def _key(self, dialog_id: str) -> str:
        return f"history:{dialog_id}"

    async def get_history(self, dialog_id: str) -> Optional[List[dict]]:
        """
        获取对话历史

        流程:
        1. 查 Redis 缓存
        2. 未命中则查 DB
        3. 写入缓存
        """
        # 1. 查 Redis
        cached = await self._redis.get(self._key(dialog_id))
        if cached:
            return json.loads(cached)

        # 2. 查 DB (延迟导入避免循环)
        from app.services.history.history import HistoryService
        from app.database.session import async_session_dependency

        async for session in async_session_dependency():
            history_service = HistoryService()
            histories = await history_service.get_history_by_dialog(session, dialog_id)

            if not histories:
                return None

            # 3. 写入缓存 (write-through)
            await self.update_cache(dialog_id, histories)

            return histories

    async def update_cache(self, dialog_id: str, histories: List) -> None:
        """
        Write-through: 更新缓存

        Args:
            dialog_id: 对话 ID
            histories: ChatHistory 对象列表
        """
        data = json.dumps([h.to_dict() for h in histories])
        await self._redis.setex(self._key(dialog_id), self._ttl, data)

    async def invalidate(self, dialog_id: str) -> None:
        """使对话历史缓存失效"""
        await self._redis.delete(self._key(dialog_id))
