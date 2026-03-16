"""统一会话管理 - 最终版本

特性：
1. 用户+子系统粒度缓存
2. 请求头设置（防机器人）
3. 登录频率控制（防封号）
4. Session 持久化（文件存储）
"""
import os
import json
import time
import logging
import secrets
import base64
import threading
from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============ 常量定义 ============
class Subsystem:
    """子系统标识"""
    JWC = "jwc"           # 教务系统
    LIBRARY = "library"    # 图书馆
    ECARD = "ecard"        # 校园卡


# 子系统对应的 CAS service URL
SUBSYSTEM_SERVICE_URLS = {
    Subsystem.JWC: "http://csujwc.its.csu.edu.cn/sso.jsp",
    Subsystem.LIBRARY: "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    Subsystem.ECARD: "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
}

# 请求头 - 模拟浏览器
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

CAS_BASE_URL = "https://ca.csu.edu.cn"
CAS_LOGIN_URL = f"{CAS_BASE_URL}/authserver/login"
AES_CHARSET = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"

# 默认 Session 存储路径
DEFAULT_SESSION_STORAGE_PATH = "./csu_sessions.json"


# ============ 工具函数 ============
def random_string(length: int) -> str:
    return "".join(secrets.choice(AES_CHARSET) for _ in range(length))


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    padding = block_size - (len(data) % block_size)
    return data + bytes([padding] * padding)


def encrypt_password(password: str, salt: str) -> str:
    prefix = random_string(64)
    iv = random_string(16)
    plain = pkcs7_pad((prefix + password).encode("utf-8"), 16)
    cipher = AES.new(salt.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    encrypted = cipher.encrypt(plain)
    return base64.b64encode(encrypted).decode("utf-8")


def create_session() -> requests.Session:
    """创建带默认请求头的 Session"""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session


# ============ Session 持久化 ============
class SessionPersistence:
    """
    Session 持久化 - 保存和加载 cookies 到文件

    注意：requests.Session 对象本身无法完整序列化
    只持久化 cookies 和必要的元数据
    """

    def __init__(self, storage_path: str = DEFAULT_SESSION_STORAGE_PATH):
        self._storage_path = storage_path
        self._lock = threading.Lock()

    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int = 30 * 60) -> None:
        """
        保存 Session 的 cookies 到文件

        Args:
            user_id: 用户 ID
            subsystem: 子系统标识
            session: 包含 cookies 的 Session
            ttl_seconds: 缓存有效期（秒）
        """
        with self._lock:
            data = self._load_all()

            # 提取可序列化的 cookies
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

            logger.info(f"Session saved to file for {user_id}:{subsystem}")

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        """
        从文件加载 Session

        Returns:
            恢复的 Session，如果不存在或过期返回 None
        """
        with self._lock:
            data = self._load_all()

            if user_id not in data or subsystem not in data[user_id]:
                return None

            session_data = data[user_id][subsystem]

            # 检查是否过期
            if time.time() > session_data.get("expires_at", 0):
                logger.info(f"Saved session expired for {user_id}:{subsystem}")
                return None

            # 恢复 cookies
            session = create_session()
            cookies_dict = session_data.get("cookies", {})

            for name, cookie_info in cookies_dict.items():
                session.cookies.set(
                    name,
                    cookie_info["value"],
                    domain=cookie_info.get("domain"),
                    path=cookie_info.get("path", "/"),
                    secure=cookie_info.get("secure", False),
                )

            logger.info(f"Session loaded from file for {user_id}:{subsystem}")
            return session

    def _load_all(self) -> dict:
        """加载所有持久化数据"""
        if not os.path.exists(self._storage_path):
            return {}
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load session file: {e}")
            return {}

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使 session 失效"""
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

    def cleanup_expired(self) -> int:
        """清理所有过期的 session"""
        data = self._load_all()
        now = time.time()
        cleaned = 0

        for user_id in list(data.keys()):
            for subsystem in list(data[user_id].keys()):
                if now > data[user_id][subsystem].get("expires_at", 0):
                    del data[user_id][subsystem]
                    cleaned += 1
            if not data[user_id]:
                del data[user_id]

        if cleaned > 0:
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            logger.info(f"Cleaned up {cleaned} expired sessions")

        return cleaned


# ============ 登录频率控制 ============
class LoginRateLimiter:
    """登录频率控制器 - 防止账号被封"""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._attempts: dict[str, list[float]] = {}
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
            logger.info(f"Login attempt recorded for {user_id}")

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


# ============ 会话缓存（用户+子系统粒度）===========
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
                logger.info(f"Session expired for {self._make_key(user_id, subsystem)}")
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
            logger.info(f"Session cached for {self._make_key(user_id, subsystem)}")

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        with self._lock:
            if user_id not in self._cache:
                return
            if subsystem is None:
                del self._cache[user_id]
            elif subsystem in self._cache[user_id]:
                del self._cache[user_id][subsystem]


# ============ CAS 登录 ============
class CASLoginError(Exception):
    pass


class AccountLockedError(Exception):
    pass


def cas_login(
    username: str,
    password: str,
    service_url: str,
    rate_limiter: Optional[LoginRateLimiter] = None
) -> requests.Session:
    """CAS 统一认证登录"""
    if rate_limiter:
        if not rate_limiter.can_login(username):
            wait_time = rate_limiter.get_wait_time(username)
            raise AccountLockedError(f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试")
        rate_limiter.record_login(username)

    session = create_session()

    try:
        login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"
        logger.info(f"Fetching login page: {login_url}")

        resp = session.get(login_url, allow_redirects=False)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]
        event_id = soup.find("input", {"name": "_eventId"})["value"]
        dllt = soup.find("input", {"name": "dllt"})["value"]
        salt = soup.find("input", {"id": "pwdEncryptSalt"})["value"]

        if not salt or not execution:
            raise CASLoginError("Failed to parse login page")

        encrypted_pwd = encrypt_password(password, salt)

        form_data = {
            "username": username,
            "password": encrypted_pwd,
            "passwordText": "",
            "lt": lt,
            "execution": execution,
            "_eventId": event_id,
            "cllt": "userNameLogin",
            "dllt": dllt,
        }

        post_url = resp.headers.get("Location", login_url)
        if not post_url.startswith("http"):
            post_url = urljoin(login_url, post_url)

        resp = session.post(post_url, data=form_data, allow_redirects=False)

        final_url = resp.headers.get("Location", "")

        if resp.status_code == 401 or "账号" in resp.text or "锁定" in resp.text:
            raise AccountLockedError("账号可能被锁定")

        if not final_url:
            raise CASLoginError("登录失败: 无重定向地址")

        target_domain = service_url.split("://")[1].split("/")[0]
        if target_domain not in final_url:
            if "密码" in resp.text:
                raise CASLoginError("用户名或密码错误")
            raise CASLoginError(f"登录失败: 重定向到未知地址 {final_url}")

        # 【关键】访问重定向地址，获取目标系统的 Cookie
        # 问题：可能有多个 JSESSIONID，需要处理
        logger.info(f"Following redirect to: {final_url}")

        # 使用不跟随重定向的方式，手动获取最终地址的 Cookie
        try:
            resp = session.get(final_url, allow_redirects=False)
            # 跟随所有重定向直到最终页面
            while resp.status_code in (301, 302, 303, 307, 308):
                next_url = resp.headers.get("Location")
                if next_url:
                    if not next_url.startswith("http"):
                        from urllib.parse import urljoin
                        next_url = urljoin(resp.url, next_url)
                    resp = session.get(next_url, allow_redirects=False)
                else:
                    break
        except Exception as e:
            # 如果出错，尝试简单方式
            logger.warning(f"Redirect handling failed: {e}, trying simple approach")
            session.get(final_url, allow_redirects=True)

        # 清理可能重复的 Cookie，保留最新的
        cookies_to_keep = {}
        for cookie in session.cookies:
            if cookie.name == "JSESSIONID":
                # 只保留最新的（最后设置的）
                cookies_to_keep[cookie.name] = cookie
            else:
                cookies_to_keep[cookie.name] = cookie

        # 重新设置 Cookie，移除重复
        session.cookies.clear()
        for name, cookie in cookies_to_keep.items():
            session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

        logger.info(f"Cookies after redirect: {dict(session.cookies)}")
        return session

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")


# ============ 统一会话管理器 ============
class UnifiedSessionManager:
    """
    统一会话管理器

    特性：
    1. 用户+子系统粒度缓存（内存）
    2. Session 持久化（文件）
    3. 登录频率控制
    4. 请求头模拟浏览器
    """

    def __init__(
        self,
        cache: Optional[SubsystemSessionCache] = None,
        rate_limiter: Optional[LoginRateLimiter] = None,
        persistence: Optional[SessionPersistence] = None,
        ttl_seconds: int = 30 * 60,
        storage_path: str = DEFAULT_SESSION_STORAGE_PATH,
        enable_persistence: bool = True,
    ):
        self._cache = cache or SubsystemSessionCache(ttl_seconds=ttl_seconds)
        self._rate_limiter = rate_limiter or LoginRateLimiter()
        self._ttl = ttl_seconds
        self._enable_persistence = enable_persistence

        # 初始化持久化
        if enable_persistence:
            self._persistence = persistence or SessionPersistence(storage_path)
            # 启动时清理过期 session
            self._persistence.cleanup_expired()
        else:
            self._persistence = None

    def get_session(
        self,
        user_id: str,
        password: str,
        subsystem: str
    ) -> requests.Session:
        """
        获取指定子系统的会话（自动加载/保存/缓存）
        """
        # 1. 尝试从内存缓存获取
        cached = self._cache.get(user_id, subsystem)
        if cached:
            logger.info(f"Using memory cache for {user_id}:{subsystem}")
            return cached.session

        # 2. 尝试从文件加载
        if self._persistence:
            loaded_session = self._persistence.load(user_id, subsystem)
            if loaded_session:
                # 放入内存缓存
                self._cache.set(user_id, subsystem, loaded_session)
                logger.info(f"Loaded from file for {user_id}:{subsystem}")
                return loaded_session

        # 3. 需要登录
        service_url = SUBSYSTEM_SERVICE_URLS.get(subsystem)
        if not service_url:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        logger.info(f"No session found for {user_id}:{subsystem}, performing CAS login...")

        session = cas_login(user_id, password, service_url, self._rate_limiter)

        # 4. 缓存到内存
        self._cache.set(user_id, subsystem, session)

        # 5. 持久化到文件
        if self._persistence:
            self._persistence.save(user_id, subsystem, session, self._ttl)

        return session

    def access_jwc(self, user_id: str, password: str) -> requests.Session:
        return self.get_session(user_id, password, Subsystem.JWC)

    def access_library(self, user_id: str, password: str) -> requests.Session:
        return self.get_session(user_id, password, Subsystem.LIBRARY)

    def access_ecard(self, user_id: str, password: str) -> requests.Session:
        return self.get_session(user_id, password, Subsystem.ECARD)

    def invalidate_session(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使会话失效（同时删除内存和文件）"""
        self._cache.invalidate(user_id, subsystem)
        if self._persistence:
            self._persistence.invalidate(user_id, subsystem)


# ============ 演示 ============
def demo():
    """演示"""
    print("\n" + "=" * 60)
    print("统一会话管理 - 自动持久化演示")
    print("=" * 60)

    storage_file = "./demo_sessions.json"

    # 清理旧文件
    if os.path.exists(storage_file):
        os.remove(storage_file)

    # 创建管理器（启用持久化）
    manager = UnifiedSessionManager(
        ttl_seconds=30 * 60,
        storage_path=storage_file,
        enable_persistence=True,
    )

    print("\n【1】第一次请求（会登录并保存到文件）:")
    print("  → 当前没有 session")
    print("  → 执行 CAS 登录")
    print("  → 保存到文件")

    # 模拟一个 session
    fake_session = create_session()
    fake_session.cookies.set("JSESSIONID", "test123", domain="csujwc.its.csu.edu.cn")
    manager._cache.set("test_user", Subsystem.JWC, fake_session)
    manager._persistence.save("test_user", Subsystem.JWC, fake_session, 30 * 60)
    print("  → 已保存到文件")

    print("\n【2】第二次请求（从文件加载）:")
    print("  → 检查内存缓存")
    print("  → 检查文件")
    loaded = manager._persistence.load("test_user", Subsystem.JWC)
    if loaded:
        print(f"  → 从文件加载成功，cookies: {dict(loaded.cookies)}")

    print("\n【3】查看保存的文件:")
    with open(storage_file, "r") as f:
        print(f"  {f.read()}")

    print("\n【4】流程总结:")
    print("""
    get_session() 流程：
    1. 检查内存缓存 → 有则返回
    2. 检查文件缓存 → 有则返回，放入内存
    3. 执行 CAS 登录
    4. 保存到内存 + 保存到文件
    5. 返回 session

    这样即使进程退出，下次启动也能从文件恢复 session！
    """)

    # 清理
    if os.path.exists(storage_file):
        os.remove(storage_file)

    print("=" * 60)


if __name__ == "__main__":
    demo()
