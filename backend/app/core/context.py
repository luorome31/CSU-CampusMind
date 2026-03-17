"""
ToolContext - 工具运行时上下文
"""
import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.session.manager import UnifiedSessionManager

logger = logging.getLogger(__name__)


class ToolContext:
    """
    工具运行时上下文，包含用户身份和会话管理

    用于在 Agent 创建时注入用户身份信息，
    工具函数通过闭包访问 ctx 中的 user_id，
    避免 user_id 暴露给大模型
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        session_manager: Optional["UnifiedSessionManager"] = None
    ):
        self.user_id = user_id
        self.session_manager = session_manager
        self._subsystem_cache: Dict[str, Any] = {}

    @property
    def is_authenticated(self) -> bool:
        """用户是否已登录"""
        return self.user_id is not None and self.session_manager is not None

    def get_subsystem_session(self, subsystem: str) -> Optional[Dict[str, Any]]:
        """
        获取子系统 session，必要时自动登录

        注意：当前版本 UnifiedSessionManager.get_session 会自动处理登录
        """
        if not self.is_authenticated:
            logger.warning(f"User not authenticated, cannot get subsystem session for {subsystem}")
            return None

        try:
            # 从 session_manager 获取 session
            session = self.session_manager.get_session(self.user_id, subsystem)
            return session
        except Exception as e:
            logger.error(f"Failed to get subsystem session for {subsystem}: {e}")
            return None


# 导出
__all__ = ["ToolContext"]
