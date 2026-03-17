"""
统一会话管理器 - 整合缓存、持久化和 CAS 登录
密码从 config settings 加载 (.env)
"""
import logging
from typing import Optional

import requests

from app.config import settings
from .cache import SubsystemSessionCache
from .persistence import SessionPersistence
from .rate_limiter import LoginRateLimiter
from . import cas_login

logger = logging.getLogger(__name__)


class Subsystem:
    """子系统标识"""
    JWC = "jwc"
    LIBRARY = "library"
    ECARD = "ecard"


# 子系统对应的 CAS service URL
SUBSYSTEM_SERVICE_URLS = {
    Subsystem.JWC: "http://csujwc.its.csu.edu.cn/sso.jsp",
    Subsystem.LIBRARY: "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    Subsystem.ECARD: "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
}


class CASCredentialsNotSetError(Exception):
    """CAS 凭证未设置错误"""
    pass


class UnifiedSessionManager:
    """
    统一会话管理器

    特性：
    1. 用户+子系统粒度缓存（内存）
    2. Session 持久化（文件/Redis）
    3. 登录频率控制
    4. CAS 凭证从配置加载
    """

    def __init__(
        self,
        persistence: SessionPersistence,
        rate_limiter: Optional[LoginRateLimiter] = None,
        ttl_seconds: int = 30 * 60,
    ):
        self._cache = SubsystemSessionCache(ttl_seconds=ttl_seconds)
        self._persistence = persistence
        self._rate_limiter = rate_limiter or LoginRateLimiter()
        self._ttl = ttl_seconds

    def get_session(self, user_id: str, subsystem: str) -> requests.Session:
        """
        获取指定子系统的会话（自动加载/保存/缓存）

        注意: user_id 参数保留用于多用户支持，
        当前版本密码从配置加载，所有用户共用同一凭证
        """
        # 1. 尝试从内存缓存获取
        cached = self._cache.get(user_id, subsystem)
        if cached:
            logger.info(f"Using memory cache for {user_id}:{subsystem}")
            return cached.session

        # 2. 尝试从文件加载
        loaded_session = self._persistence.load(user_id, subsystem)
        if loaded_session:
            self._cache.set(user_id, subsystem, loaded_session)
            logger.info(f"Loaded from file for {user_id}:{subsystem}")
            return loaded_session

        # 3. 需要登录 - 从配置获取密码
        username = settings.cas_username
        password = settings.cas_password

        if not username or not password:
            raise CASCredentialsNotSetError(
                "CAS 凭证未设置，请在 .env 文件中配置 CAS_USERNAME 和 CAS_PASSWORD"
            )

        service_url = SUBSYSTEM_SERVICE_URLS.get(subsystem)
        if not service_url:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        logger.info(f"No session found for {user_id}:{subsystem}, performing CAS login...")

        session = cas_login.cas_login(
            username,
            password,
            service_url,
            self._rate_limiter
        )

        # 4. 缓存到内存
        self._cache.set(user_id, subsystem, session)

        # 5. 持久化到文件
        self._persistence.save(user_id, subsystem, session, self._ttl)

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

    def invalidate_session(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使会话失效"""
        self._cache.invalidate(user_id, subsystem)
        self._persistence.invalidate(user_id, subsystem)
