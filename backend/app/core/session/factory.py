# backend/app/core/session/factory.py
"""
全局 SessionManager 工厂函数
"""
import logging
from typing import Optional

from app.config import settings
from app.core.session import (
    UnifiedSessionManager,
    FileSessionPersistence,
    PasswordManager,
    LoginRateLimiter,
)

logger = logging.getLogger(__name__)

# 全局实例
_session_manager: Optional[UnifiedSessionManager] = None


def get_session_manager() -> UnifiedSessionManager:
    """获取全局 SessionManager 实例（单例）"""
    global _session_manager

    if _session_manager is None:
        _session_manager = create_session_manager()

    return _session_manager


def create_session_manager() -> UnifiedSessionManager:
    """创建 SessionManager 实例"""
    persistence = FileSessionPersistence(
        storage_path=settings.session_storage_path
    )

    password_manager = PasswordManager(
        storage_path=settings.password_storage_path,
        encryption_key=settings.password_encryption_key
    )

    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        password_manager=password_manager,
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=settings.session_ttl_seconds,
    )

    logger.info("SessionManager 实例已创建")
    return manager


def reset_session_manager():
    """重置 SessionManager（用于测试）"""
    global _session_manager
    _session_manager = None
