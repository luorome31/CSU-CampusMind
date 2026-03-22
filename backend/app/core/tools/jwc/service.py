"""
教务系统服务 - 整合 SessionManager 和 JwcClient
"""
import logging
from typing import List

from app.core.session.manager import UnifiedSessionManager
from .client import Grade, ClassEntry, RankEntry, LevelExamEntry, JwcClient

logger = logging.getLogger(__name__)


class JwcService:
    """教务系统服务入口"""

    def __init__(self, session_manager: UnifiedSessionManager):
        self._session_manager = session_manager

    async def _get_client(self, user_id: str) -> JwcClient:
        """获取 JwcClient 实例"""
        session = await self._session_manager.get_jwc_session(user_id)
        return JwcClient(session)

    async def get_grades(self, user_id: str, term: str = "") -> List[Grade]:
        """
        查询成绩

        Args:
            user_id: 用户 ID
            term: 学期，如 "2024-2025-1"，空则查全部

        Returns:
            成绩列表
        """
        client = await self._get_client(user_id)
        return client.get_grades(term)

    async def get_schedule(self, user_id: str, term: str, week: str = "0") -> tuple[List[ClassEntry], str]:
        """
        查询课表

        Args:
            user_id: 用户 ID
            term: 学期，如 "2024-2025-1"
            week: 周次，"0" 为全部周

        Returns:
            (课表列表, 学期开始日期)
        """
        client = await self._get_client(user_id)
        return client.get_class_schedule(term, week)

    async def get_rank(self, user_id: str) -> List[RankEntry]:
        """查询专业排名"""
        client = await self._get_client(user_id)
        return client.get_rank()

    async def get_level_exams(self, user_id: str) -> List[LevelExamEntry]:
        """查询等级考试成绩"""
        client = await self._get_client(user_id)
        return client.get_level_exams()
