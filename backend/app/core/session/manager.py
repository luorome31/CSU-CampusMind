"""
统一会话管理器 - 整合缓存、持久化和 CAS 登录

CAS 登录流程:
1. 用户登录 CAS 获取 CASTGC cookie (跨子系统共享)
2. 使用 CASTGC 通过 SubsystemSessionProvider 获取各子系统的 session
"""
import json
import logging
import time
from typing import Optional

import requests

from app.config import settings
from .persistence import SessionPersistence
from .rate_limiter import LoginRateLimiter
from . import cas_login
from .providers.base import SubsystemSessionProvider

logger = logging.getLogger(__name__)


class Subsystem:
    """子系统标识"""
    JWC = "jwc"
    LIBRARY = "library"
    ECARD = "ecard"
    OA = "oa"


# 子系统对应的 CAS service URL
SUBSYSTEM_SERVICE_URLS = {
    Subsystem.JWC: "http://csujwc.its.csu.edu.cn/sso.jsp",
    Subsystem.LIBRARY: "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    Subsystem.ECARD: "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
    Subsystem.OA: "https://oa.csu.edu.cn/con/",
}


class CASCredentialsNotSetError(Exception):
    """CAS 凭证未设置错误"""
    pass


class NeedReLoginError(Exception):
    """需要重新登录错误（CASTGC 过期或不存在）"""
    pass


class UnifiedSessionManager:
    """
    统一会话管理器

    特性：
    1. CASTGC 跨子系统共享（用户级别，TTL 2小时）
    2. 子系统 Session 独立存储（通过 SubsystemSessionProvider 获取）
    3. Session 持久化（文件）
    4. 登录频率控制
    """

    def __init__(
        self,
        persistence: SessionPersistence,
        rate_limiter: Optional[LoginRateLimiter] = None,
        ttl_seconds: int = 30 * 60,
    ):
        self._persistence = persistence
        self._rate_limiter = rate_limiter or LoginRateLimiter()
        self._ttl = ttl_seconds

    def _castgc_key(self, user_id: str) -> str:
        """Build Redis key for CASTGC storage"""
        return f"castgc:{user_id}"

    def _get_castgc(self, user_id: str) -> Optional[str]:
        """
        获取缓存的 CASTGC cookie

        Returns:
            CASTGC 值，如果不存在或过期返回 None
        """
        data = self._persistence._redis.get(self._castgc_key(user_id))
        if not data:
            return None
        try:
            castgc_data = json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Corrupted CASTGC data for user {user_id}, discarding")
            self._persistence._redis.delete(self._castgc_key(user_id))
            return None
        if time.time() > castgc_data.get("expires_at", 0):
            self._persistence._redis.delete(self._castgc_key(user_id))
            return None
        return castgc_data.get("castgc")

    def _save_castgc(self, user_id: str, castgc: str) -> None:
        """保存 CASTGC cookie，TTL 4小时"""
        data = json.dumps({
            "castgc": castgc,
            "created_at": time.time(),
            "expires_at": time.time() + 4 * 3600,  # 4 hours TTL
        })
        self._persistence._redis.setex(self._castgc_key(user_id), 4 * 3600, data)

    def login(self, user_id: str, username: str, password: str) -> None:
        """
        用户登录 CAS，获取 CASTGC

        Args:
            user_id: 用户 ID (通常是 username)
            username: CAS 用户名
            password: CAS 密码

        Raises:
            AccountLockedError: 账号被锁定
            CASLoginError: 登录失败
        """
        castgc = cas_login.cas_login_only_castgc(username, password, self._rate_limiter)
        self._save_castgc(user_id, castgc)
        logger.info(f"User {user_id} logged in, CASTGC saved")

    def get_session(self, user_id: str, subsystem: str) -> requests.Session:
        """
        获取指定子系统的会话

        流程：
        1. 检查持久化缓存 → 存在且有效? → 直接返回
        2. 获取 CASTGC
        3. 若无 CASTGC，抛出 NeedReLoginError
        4. 使用 SubsystemSessionProvider 获取子系统 session
        5. 持久化保存 session

        Raises:
            NeedReLoginError: CASTGC 不存在或过期，需要重新登录
        """
        # 1. 检查持久化缓存
        loaded_session = self._persistence.load(user_id, subsystem)
        if loaded_session:
            logger.info(f"Loaded session from persistence for {user_id}:{subsystem}")
            return loaded_session

        # 2. 获取 CASTGC
        castgc = self._get_castgc(user_id)
        if not castgc:
            raise NeedReLoginError(
                f"用户 {user_id} 的 CASTGC 已过期或不存在，请重新登录"
            )

        # 3. 使用 Provider 获取子系统 session
        provider = SubsystemSessionProvider.get_provider(subsystem)
        session = provider.fetch_session(castgc)

        # 4. 持久化保存
        self._persistence.save(user_id, subsystem, session, self._ttl)

        logger.info(f"Fetched new session for {user_id}:{subsystem}")
        return session

    def get_jwc_session(self, user_id: str) -> requests.Session:
        """获取教务系统 Session"""
        return self.get_session(user_id, Subsystem.JWC)

    def get_library_session(self, user_id: str) -> requests.Session:
        """获取图书馆 Session"""
        return self.get_session(user_id, Subsystem.LIBRARY)

    def get_ecard_session(self, user_id: str) -> requests.Session:
        """获取校园卡 Session"""
        return self.get_session(user_id, Subsystem.ECARD)

    def get_oa_session(self, user_id: str) -> requests.Session:
        """获取办公网 Session"""
        return self.get_session(user_id, Subsystem.OA)

    def invalidate_session(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使会话失效"""
        self._persistence.invalidate(user_id, subsystem)
        # 如果指定 subsystem 为 None，清除所有子系统的 session，同时也清除 CASTGC
        if subsystem is None:
            self._persistence._redis.delete(self._castgc_key(user_id))
