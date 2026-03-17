# 教务系统工具集成实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 LangGraph React Agent 中接入教务系统业务查询工具，实现多用户 Session 管理和业务数据查询

**Architecture:** 采用中等耦合架构 - Session 管理与业务逻辑分离，预留 Redis 接口

**Tech Stack:** Python 3.11+, requests, beautifulsoup4, pycryptodome, langchain

---

## 文件结构

```
backend/app/
├── core/
│   ├── session/                    # 新增：会话管理模块
│   │   ├── __init__.py
│   │   ├── cache.py                # SubsystemSessionCache
│   │   ├── rate_limiter.py         # LoginRateLimiter
│   │   ├── persistence.py          # SessionPersistence (文件/Redis)
│   │   ├── password.py             # PasswordManager
│   │   ├── cas_login.py            # CAS 登录逻辑
│   │   └── manager.py              # UnifiedSessionManager
│   │
│   └── tools/
│       └── jwc/                    # 新增：教务系统工具
│           ├── __init__.py
│           ├── client.py           # JwcClient + 数据模型
│           ├── service.py          # JwcService
│           └── tools.py            # LangChain Tools 封装
```

---

## Chunk 1: SessionManager 模块

### Task 1.1: 创建模块目录和基础结构

**Files:**
- Create: `backend/app/core/session/__init__.py`
- Create: `backend/app/core/session/cache.py`
- Test: `backend/tests/core/session/test_cache.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p backend/app/core/session
mkdir -p backend/tests/core/session
```

- [ ] **Step 2: 编写 SubsystemSessionCache 测试**

```python
# backend/tests/core/session/test_cache.py
import pytest
from dataclasses import dataclass
from app.core.session.cache import SubsystemSessionCache, CachedSession
import requests
import time

def test_cache_get_miss():
    cache = SubsystemSessionCache(ttl_seconds=60)
    result = cache.get("user1", "jwc")
    assert result is None

def test_cache_set_and_get():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    cached = cache.get("user1", "jwc")
    assert cached is not None
    assert cached.session is session

def test_cache_key_separation():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session1 = requests.Session()
    session2 = requests.Session()
    cache.set("user1", "jwc", session1)
    cache.set("user2", "jwc", session2)

    assert cache.get("user1", "jwc").session is session1
    assert cache.get("user2", "jwc").session is session2

def test_cache_expiration():
    cache = SubsystemSessionCache(ttl_seconds=1)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    time.sleep(1.1)
    result = cache.get("user1", "jwc")
    assert result is None

def test_invalidate():
    cache = SubsystemSessionCache(ttl_seconds=60)
    session = requests.Session()
    cache.set("user1", "jwc", session)

    cache.invalidate("user1", "jwc")
    assert cache.get("user1", "jwc") is None
```

- [ ] **Step 3: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/session/test_cache.py -v`
Expected: FAIL (import error - module not found)

- [ ] **Step 4: 实现 SubsystemSessionCache**

```python
# backend/app/core/session/cache.py
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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/session/test_cache.py -v`
Expected: PASS

- [ ] **Step 6: 提交代码**

```bash
cd backend
git add app/core/session/__init__.py app/core/session/cache.py tests/core/session/test_cache.py
git commit -m "feat(session): add SubsystemSessionCache for user+subsystem session caching"
```

---

### Task 1.2: LoginRateLimiter

**Files:**
- Create: `backend/app/core/session/rate_limiter.py`
- Test: `backend/tests/core/session/test_rate_limiter.py`

- [ ] **Step 1: 编写 LoginRateLimiter 测试**

```python
# backend/tests/core/session/test_rate_limiter.py
import pytest
import time
from app.core.session.rate_limiter import LoginRateLimiter

def test_can_login_initially():
    limiter = LoginRateLimiter(max_attempts=5, window_seconds=60)
    assert limiter.can_login("user1") is True

def test_login_blocks_after_limit():
    limiter = LoginRateLimiter(max_attempts=3, window_seconds=60)

    for _ in range(3):
        limiter.record_login("user1")

    assert limiter.can_login("user1") is False

def test_wait_time_calculation():
    limiter = LoginRateLimiter(max_attempts=2, window_seconds=60)

    limiter.record_login("user1")
    limiter.record_login("user1")

    wait = limiter.get_wait_time("user1")
    assert 0 < wait <= 60

def test_window_cleanup():
    limiter = LoginRateLimiter(max_attempts=5, window_seconds=1)

    limiter.record_login("user1")
    time.sleep(1.1)

    assert limiter.can_login("user1") is True
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/session/test_rate_limiter.py -v`
Expected: FAIL (import error)

- [ ] **Step 3: 实现 LoginRateLimiter**

```python
# backend/app/core/session/rate_limiter.py
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/session/test_rate_limiter.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
cd backend
git add app/core/session/rate_limiter.py tests/core/session/test_rate_limiter.py
git commit -m "feat(session): add LoginRateLimiter for login frequency control"
```

---

### Task 1.3: SessionPersistence (文件存储)

**Files:**
- Create: `backend/app/core/session/persistence.py`
- Test: `backend/tests/core/session/test_persistence.py`

- [ ] **Step 1: 添加依赖到 pyproject.toml**

```toml
# backend/pyproject.toml - 添加到 dependencies
requests = ">=2.31.0"
beautifulsoup4 = ">=4.12.0"
pycryptodome = ">=3.19.0"
```

- [ ] **Step 2: 编写 SessionPersistence 测试**

```python
# backend/tests/core/session/test_persistence.py
import pytest
import os
import tempfile
import json
from app.core.session.persistence import FileSessionPersistence
import requests

def test_save_and_load():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        session = requests.Session()
        session.cookies.set("JSESSIONID", "test123", domain="example.com")

        persistence.save("user1", "jwc", session, ttl_seconds=60)

        loaded = persistence.load("user1", "jwc")
        assert loaded is not None
        assert loaded.cookies.get("JSESSIONID").value == "test123"
    finally:
        os.unlink(temp_path)

def test_load_missing():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        result = persistence.load("user1", "jwc")
        assert result is None
    finally:
        os.unlink(temp_path)

def test_expiration():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        persistence = FileSessionPersistence(storage_path=temp_path)
        session = requests.Session()
        session.cookies.set("test", "value")

        # 保存一个过期的 session (expires_at = now - 1)
        data = {"user1": {"jwc": {"cookies": {"test": {"value": "value"}}, "saved_at": 0, "expires_at": 0}}}
        with open(temp_path, 'w') as f:
            json.dump(data, f)

        result = persistence.load("user1", "jwc")
        assert result is None
    finally:
        os.unlink(temp_path)
```

- [ ] **Step 3: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/session/test_persistence.py -v`
Expected: FAIL (import error)

- [ ] **Step 4: 实现 FileSessionPersistence**

```python
# backend/app/core/session/persistence.py
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
    """文件存储 Session 持久化"""

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
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/session/test_persistence.py -v`
Expected: PASS

- [ ] **Step 6: 提交代码**

```bash
cd backend
git add pyproject.toml app/core/session/persistence.py tests/core/session/test_persistence.py
git commit -m "feat(session): add FileSessionPersistence for session storage"
```

---

### Task 1.4: PasswordManager

**Files:**
- Create: `backend/app/core/session/password.py`
- Test: `backend/tests/core/session/test_password.py`

- [ ] **Step 1: 编写 PasswordManager 测试**

```python
# backend/tests/core/session/test_password.py
import pytest
import os
import tempfile
from app.core.session.password import PasswordManager

def test_save_and_retrieve():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        manager.save_password("user1", "mypassword")

        password = manager.get_password("user1")
        assert password == "mypassword"
    finally:
        os.unlink(temp_path)

def test_get_missing():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        password = manager.get_password("nonexistent")
        assert password is None
    finally:
        os.unlink(temp_path)

def test_delete():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name

    try:
        manager = PasswordManager(storage_path=temp_path, encryption_key="test-key-12345")
        manager.save_password("user1", "mypassword")
        manager.delete_password("user1")

        password = manager.get_password("user1")
        assert password is None
    finally:
        os.unlink(temp_path)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/session/test_password.py -v`
Expected: FAIL (import error)

- [ ] **Step 3: 实现 PasswordManager**

```python
# backend/app/core/session/password.py
import os
import json
import base64
import threading
from typing import Optional
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


class PasswordManager:
    """CAS 密码加密存储"""

    def __init__(self, storage_path: str = "./data/csu_passwords.json", encryption_key: str = ""):
        self._storage_path = storage_path
        self._encryption_key = encryption_key.encode('utf-8') if encryption_key else b"default-key-change-me"
        self._lock = threading.Lock()

        # 确保目录存在
        os.makedirs(os.path.dirname(storage_path) or ".", exist_ok=True)

    def _encrypt(self, password: str) -> str:
        """AES 加密"""
        cipher = AES.new(self._encryption_key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(password.encode('utf-8'))
        return base64.b64encode(cipher.nonce + ciphertext + tag).decode('utf-8')

    def _decrypt(self, encrypted: str) -> str:
        """AES 解密"""
        data = base64.b64decode(encrypted.encode('utf-8'))
        nonce = data[:16]
        ciphertext = data[16:-16]
        tag = data[-16:]

        cipher = AES.new(self._encryption_key, AES.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')

    def save_password(self, user_id: str, password: str) -> None:
        with self._lock:
            data = self._load_all()
            data[user_id] = self._encrypt(password)
            self._save_all(data)

    def get_password(self, user_id: str) -> Optional[str]:
        with self._lock:
            data = self._load_all()
            if user_id not in data:
                return None
            return self._decrypt(data[user_id])

    def delete_password(self, user_id: str) -> None:
        with self._lock:
            data = self._load_all()
            if user_id in data:
                del data[user_id]
                self._save_all(data)

    def _load_all(self) -> dict:
        if not os.path.exists(self._storage_path):
            return {}
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def _save_all(self, data: dict) -> None:
        with open(self._storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/session/test_password.py -v`
Expected: PASS

- [ ] **Step 5: 提交代码**

```bash
cd backend
git add app/core/session/password.py tests/core/session/test_password.py
git commit -m "feat(session): add PasswordManager for encrypted password storage"
```

---

### Task 1.5: CAS 登录逻辑

**Files:**
- Create: `backend/app/core/session/cas_login.py`

- [ ] **Step 1: 参考代码实现 CAS 登录**

从 `/home/luorome/software/CampusMind/scripts/csu_system_scripts/unified_session_v2.py` 中提取 CAS 登录逻辑

```python
# backend/app/core/session/cas_login.py
"""
CAS 登录逻辑 - 参考 unified_session_v2.py 实现
"""
import secrets
import base64
import logging
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES

logger = logging.getLogger(__name__)

# 常量定义
CAS_BASE_URL = "https://ca.csu.edu.cn"
CAS_LOGIN_URL = f"{CAS_BASE_URL}/authserver/login"
AES_CHARSET = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

# 子系统 CAS service URL
SUBSYSTEM_SERVICE_URLS = {
    "jwc": "http://csujwc.its.csu.edu.cn/sso.jsp",
    "library": "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp",
    "ecard": "https://ecard.csu.edu.cn/berserker-auth/cas/login/wisedu?targetUrl=https://ecard.csu.edu.cn/plat-pc/?name=loginTransit",
}


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


class CASLoginError(Exception):
    """CAS 登录错误"""
    pass


class AccountLockedError(Exception):
    """账号被锁定错误"""
    pass


def cas_login(
    username: str,
    password: str,
    service_url: str,
    rate_limiter=None
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

        # 访问重定向地址，获取目标系统的 Cookie
        logger.info(f"Following redirect to: {final_url}")

        try:
            resp = session.get(final_url, allow_redirects=False)
            while resp.status_code in (301, 302, 303, 307, 308):
                next_url = resp.headers.get("Location")
                if next_url:
                    if not next_url.startswith("http"):
                        next_url = urljoin(resp.url, next_url)
                    resp = session.get(next_url, allow_redirects=False)
                else:
                    break
        except Exception as e:
            logger.warning(f"Redirect handling failed: {e}, trying simple approach")
            session.get(final_url, allow_redirects=True)

        # 清理可能重复的 Cookie
        cookies_to_keep = {}
        for cookie in session.cookies:
            if cookie.name == "JSESSIONID":
                cookies_to_keep[cookie.name] = cookie
            else:
                cookies_to_keep[cookie.name] = cookie

        session.cookies.clear()
        for name, cookie in cookies_to_keep.items():
            session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)

        logger.info(f"Cookies after redirect: {dict(session.cookies)}")
        return session

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")
```

- [ ] **Step 2: 提交代码**

```bash
cd backend
git add app/core/session/cas_login.py
git commit -m "feat(session): add CAS login logic"
```

---

### Task 1.6: UnifiedSessionManager

**Files:**
- Create: `backend/app/core/session/manager.py`
- Test: `backend/tests/core/session/test_manager.py`

- [ ] **Step 1: 编写 UnifiedSessionManager 测试（Mock 模式）**

```python
# backend/tests/core/session/test_manager.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.core.session.manager import UnifiedSessionManager
from app.core.session.cache import SubsystemSessionCache
from app.core.session.persistence import FileSessionPersistence
from app.core.session.password import PasswordManager
from app.core.session.rate_limiter import LoginRateLimiter
import requests

@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def manager(temp_dir):
    session_path = os.path.join(temp_dir, "sessions.json")
    password_path = os.path.join(temp_dir, "passwords.json")

    cache = SubsystemSessionCache(ttl_seconds=60)
    persistence = FileSessionPersistence(storage_path=session_path)
    password_mgr = PasswordManager(storage_path=password_path, encryption_key="test-key")
    rate_limiter = LoginRateLimiter()

    return UnifiedSessionManager(
        password_manager=password_mgr,
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

def test_set_password(manager):
    manager.set_password("user1", "mypassword")
    # 验证密码已保存
    assert manager._password_manager.get_password("user1") == "mypassword"

def test_get_session_no_password(manager):
    """无密码时应抛出异常"""
    with pytest.raises(ValueError, match="请先设置密码"):
        manager.get_session("user1", "jwc")

@patch('app.core.session.manager.cas_login')
def test_get_session_with_password(mock_cas_login, manager):
    """有密码时应调用 CAS 登录"""
    manager.set_password("user1", "mypassword")

    mock_session = requests.Session()
    mock_session.cookies.set("JSESSIONID", "test123")
    mock_cas_login.return_value = mock_session

    session = manager.get_session("user1", "jwc")

    assert session is not None
    mock_cas_login.assert_called_once()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/session/test_manager.py -v`
Expected: FAIL (import error)

- [ ] **Step 3: 实现 UnifiedSessionManager**

```python
# backend/app/core/session/manager.py
"""
统一会话管理器 - 整合缓存、持久化、密码管理和 CAS 登录
"""
import logging
from typing import Optional

import requests

from .cache import SubsystemSessionCache
from .persistence import SessionPersistence
from .password import PasswordManager
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


class PasswordNotSetError(Exception):
    """密码未设置错误"""
    pass


class UnifiedSessionManager:
    """
    统一会话管理器

    特性：
    1. 用户+子系统粒度缓存（内存）
    2. Session 持久化（文件/Redis）
    3. 登录频率控制
    4. CAS 密码加密存储
    """

    def __init__(
        self,
        password_manager: PasswordManager,
        persistence: SessionPersistence,
        rate_limiter: Optional[LoginRateLimiter] = None,
        ttl_seconds: int = 30 * 60,
    ):
        self._cache = SubsystemSessionCache(ttl_seconds=ttl_seconds)
        self._persistence = persistence
        self._password_manager = password_manager
        self._rate_limiter = rate_limiter or LoginRateLimiter()
        self._ttl = ttl_seconds

    def set_password(self, user_id: str, password: str) -> None:
        """存储用户 CAS 密码"""
        self._password_manager.save_password(user_id, password)

    def get_password(self, user_id: str) -> Optional[str]:
        """获取用户密码"""
        return self._password_manager.get_password(user_id)

    def delete_password(self, user_id: str) -> None:
        """删除用户密码"""
        self._password_manager.delete_password(user_id)

    def get_session(self, user_id: str, subsystem: str) -> requests.Session:
        """
        获取指定子系统的会话（自动加载/保存/缓存）
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

        # 3. 需要登录
        password = self._password_manager.get_password(user_id)
        if not password:
            raise PasswordNotSetError(f"用户 {user_id} 未设置密码，请先调用 set_password()")

        service_url = SUBSYSTEM_SERVICE_URLS.get(subsystem)
        if not service_url:
            raise ValueError(f"Unknown subsystem: {subsystem}")

        logger.info(f"No session found for {user_id}:{subsystem}, performing CAS login...")

        session = cas_login.cas_login(
            user_id,
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
```

- [ ] **Step 4: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/session/test_manager.py -v`
Expected: PASS

- [ ] **Step 5: 更新 __init__.py**

```python
# backend/app/core/session/__init__.py
from .cache import SubsystemSessionCache, CachedSession
from .rate_limiter import LoginRateLimiter
from .persistence import SessionPersistence, FileSessionPersistence
from .password import PasswordManager
from .cas_login import CASLoginError, AccountLockedError, SUBSYSTEM_SERVICE_URLS
from .manager import UnifiedSessionManager, Subsystem, PasswordNotSetError

__all__ = [
    "SubsystemSessionCache",
    "CachedSession",
    "LoginRateLimiter",
    "SessionPersistence",
    "FileSessionPersistence",
    "PasswordManager",
    "CASLoginError",
    "AccountLockedError",
    "SUBSYSTEM_SERVICE_URLS",
    "UnifiedSessionManager",
    "Subsystem",
    "PasswordNotSetError",
]
```

- [ ] **Step 6: 提交代码**

```bash
cd backend
git add app/core/session/manager.py app/core/session/__init__.py tests/core/session/test_manager.py
git commit -m "feat(session): add UnifiedSessionManager integrating all components"
```

---

## Chunk 2: JwcService 模块

### Task 2.1: 创建目录和 JwcClient

**Files:**
- Create: `backend/app/core/tools/jwc/__init__.py`
- Create: `backend/app/core/tools/jwc/client.py`
- Test: `backend/tests/core/tools/jwc/test_client.py`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p backend/app/core/tools/jwc
mkdir -p backend/tests/core/tools/jwc
```

- [ ] **Step 2: 编写测试**

```python
# backend/tests/core/tools/jwc/test_client.py
import pytest
from unittest.mock import Mock, patch
from app.core.tools.jwc.client import Grade, ClassEntry, RankEntry, JwcClient

def test_grade_dataclass():
    grade = Grade(
        term="2024-2025-1",
        course_name="高等数学",
        score="95",
        credit="4.0",
        attribute="必修",
        nature="考试"
    )
    assert grade.term == "2024-2025-1"
    assert grade.score == "95"

def test_class_entry_dataclass():
    entry = ClassEntry(
        course_name="数据结构",
        teacher="张三",
        weeks="1-16",
        place="教学楼A101",
        day_of_week="周一",
        time_of_day="1-2节"
    )
    assert entry.course_name == "数据结构"
```

- [ ] **Step 3: 运行测试确认失败**

Run: `cd backend && python -m pytest tests/core/tools/jwc/test_client.py -v`
Expected: FAIL (module not found)

- [ ] **Step 4: 实现数据模型和 JwcClient**

```python
# backend/app/core/tools/jwc/client.py
"""
教务系统业务客户端 - 从参考代码 jwc_client.py 移植
"""
import logging
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ============ 常量定义 ============
JWC_BASE_URL = "http://csujwc.its.csu.edu.cn/jsxsd"

URLS = {
    "grade": f"{JWC_BASE_URL}/kscj/yscjcx_list",
    "rank": f"{JWC_BASE_URL}/kscj/zybm_cx",
    "class": f"{JWC_BASE_URL}/xskb/xskb_list.do",
    "level_exam": f"{JWC_BASE_URL}/kscj/djkscj_list",
    "student_info": f"{JWC_BASE_URL}/grxx/xsxx",
    "student_plan": f"{JWC_BASE_URL}/pyfa/pyfa_query",
}


# ============ 数据模型 ============
@dataclass
class Grade:
    """成绩"""
    term: str
    course_name: str
    score: str
    credit: str
    attribute: str
    nature: str


@dataclass
class RankEntry:
    """排名"""
    term: str
    total_score: str
    class_rank: str
    average_score: str


@dataclass
class ClassEntry:
    """课表条目"""
    course_name: str
    teacher: str
    weeks: str
    place: str
    day_of_week: str
    time_of_day: str


@dataclass
class LevelExamEntry:
    """等级考试"""
    course: str
    written_score: str
    computer_score: str
    total_score: str
    written_level: str
    computer_level: str
    total_level: str
    exam_date: str


# ============ JwcClient ============
class JwcClient:
    """教务系统客户端"""

    def __init__(self, session: requests.Session):
        self._session = session

    def get_grades(self, term: str = "") -> List[Grade]:
        """查询成绩"""
        url = URLS["grade"]
        data = {"xnxq01id": term} if term else {}

        resp = self._session.post(url, data=data)
        html = resp.text

        if "学生个人考试成绩" not in html:
            raise Exception("成绩查询失败，可能 Cookie 已失效")

        soup = BeautifulSoup(html, "html.parser")
        grades = []

        for row in soup.select("table#dataList tr"):
            cells = row.find_all("td")
            if len(cells) < 9:
                continue

            grades.append(Grade(
                term=cells[3].get_text(strip=True),
                course_name=cells[4].get_text(strip=True),
                score=cells[5].get_text(strip=True),
                credit=cells[6].get_text(strip=True),
                attribute=cells[7].get_text(strip=True),
                nature=cells[8].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(grades)} 条成绩记录")
        return grades

    def get_rank(self) -> List[RankEntry]:
        """查询专业排名"""
        url = URLS["rank"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        ranks = []

        for option in soup.select("select[name='xqfw'] option"):
            term = option.get_text(strip=True)
            if not term:
                continue

            form = {"xqfw": term}
            rank_resp = self._session.post(url, data=form)
            rank_html = rank_resp.text

            rank_soup = BeautifulSoup(rank_html, "html.parser")
            rows = rank_soup.select("table#table1 tr")

            for row in rows[1:]:
                cells = row.find_all("td")
                if len(cells) >= 4:
                    ranks.append(RankEntry(
                        term=term,
                        total_score=cells[1].get_text(strip=True),
                        class_rank=cells[2].get_text(strip=True),
                        average_score=cells[3].get_text(strip=True),
                    ))

        logger.info(f"查询到 {len(ranks)} 条排名记录")
        return ranks

    def get_class_schedule(self, term: str, week: str = "0") -> List[ClassEntry]:
        """查询课表"""
        url = URLS["class"]
        data = {"xnxq01id": term, "zc": week}

        resp = self._session.post(url, data=data)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        classes = []

        for row in soup.select("table#table1 tr"):
            cells = row.find_all("td")
            if len(cells) < 6:
                continue

            classes.append(ClassEntry(
                course_name=cells[1].get_text(strip=True),
                teacher=cells[2].get_text(strip=True),
                weeks=cells[3].get_text(strip=True),
                place=cells[4].get_text(strip=True),
                day_of_week=cells[5].get_text(strip=True),
                time_of_day=cells[6].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(classes)} 条课表记录")
        return classes

    def get_level_exams(self) -> List[LevelExamEntry]:
        """查询等级考试成绩"""
        url = URLS["level_exam"]
        resp = self._session.get(url)
        html = resp.text

        soup = BeautifulSoup(html, "html.parser")
        exams = []

        for row in soup.select("table#dataList tr"):
            cells = row.find_all("td")
            if len(cells) < 8:
                continue

            exams.append(LevelExamEntry(
                course=cells[0].get_text(strip=True),
                written_score=cells[1].get_text(strip=True),
                computer_score=cells[2].get_text(strip=True),
                total_score=cells[3].get_text(strip=True),
                written_level=cells[4].get_text(strip=True),
                computer_level=cells[5].get_text(strip=True),
                total_level=cells[6].get_text(strip=True),
                exam_date=cells[7].get_text(strip=True),
            ))

        logger.info(f"查询到 {len(exams)} 条等级考试记录")
        return exams
```

- [ ] **Step 5: 运行测试确认通过**

Run: `cd backend && python -m pytest tests/core/tools/jwc/test_client.py -v`
Expected: PASS

- [ ] **Step 6: 提交代码**

```bash
cd backend
git add app/core/tools/jwc/client.py tests/core/tools/jwc/test_client.py
git commit -m "feat(jwc): add JwcClient with data models"
```

---

### Task 2.2: JwcService

**Files:**
- Create: `backend/app/core/tools/jwc/service.py`

- [ ] **Step 1: 实现 JwcService**

```python
# backend/app/core/tools/jwc/service.py
"""
教务系统服务 - 整合 SessionManager 和 JwcClient
"""
import logging
from typing import List, Optional

from app.core.session.manager import UnifiedSessionManager
from .client import Grade, ClassEntry, RankEntry, LevelExamEntry, JwcClient

logger = logging.getLogger(__name__)


class JwcService:
    """教务系统服务入口"""

    def __init__(self, session_manager: UnifiedSessionManager):
        self._session_manager = session_manager

    def _get_client(self, user_id: str) -> JwcClient:
        """获取 JwcClient 实例"""
        session = self._session_manager.get_jwc_session(user_id)
        return JwcClient(session)

    def get_grades(self, user_id: str, term: str = "") -> List[Grade]:
        """
        查询成绩

        Args:
            user_id: 用户 ID
            term: 学期，如 "2024-2025-1"，空则查全部

        Returns:
            成绩列表
        """
        client = self._get_client(user_id)
        return client.get_grades(term)

    def get_schedule(self, user_id: str, term: str, week: str = "0") -> List[ClassEntry]:
        """
        查询课表

        Args:
            user_id: 用户 ID
            term: 学期，如 "2024-2025-1"
            week: 周次，"0" 为全部周

        Returns:
            课表列表
        """
        client = self._get_client(user_id)
        return client.get_class_schedule(term, week)

    def get_rank(self, user_id: str) -> List[RankEntry]:
        """查询专业排名"""
        client = self._get_client(user_id)
        return client.get_rank()

    def get_level_exams(self, user_id: str) -> List[LevelExamEntry]:
        """查询等级考试成绩"""
        client = self._get_client(user_id)
        return client.get_level_exams()
```

- [ ] **Step 2: 更新 __init__.py**

```python
# backend/app/core/tools/jwc/__init__.py
from .client import Grade, ClassEntry, RankEntry, LevelExamEntry, JwcClient
from .service import JwcService

__all__ = [
    "Grade",
    "ClassEntry",
    "RankEntry",
    "LevelExamEntry",
    "JwcClient",
    "JwcService",
]
```

- [ ] **Step 3: 提交代码**

```bash
cd backend
git add app/core/tools/jwc/service.py app/core/tools/jwc/__init__.py
git commit -m "feat(jwc): add JwcService integration layer"
```

---

## Chunk 3: LangChain Tools

### Task 3.1: 创建 LangChain Tools

**Files:**
- Create: `backend/app/core/tools/jwc/tools.py`

- [ ] **Step 1: 实现 LangChain Tools**

```python
# backend/app/core/tools/jwc/tools.py
"""
LangChain Tools 封装
"""
import json
import logging
from typing import Type, Optional

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field

from app.core.session.manager import UnifiedSessionManager
from .service import JwcService, Grade, ClassEntry, RankEntry, LevelExamEntry

logger = logging.getLogger(__name__)

# 全局 SessionManager 实例（后续可注入）
_session_manager: Optional[UnifiedSessionManager] = None


def set_session_manager(manager: UnifiedSessionManager):
    """设置全局 SessionManager"""
    global _session_manager
    _session_manager = manager


def get_session_manager() -> UnifiedSessionManager:
    """获取全局 SessionManager"""
    if _session_manager is None:
        raise RuntimeError("SessionManager 未设置，请先调用 set_session_manager()")
    return _session_manager


# ============ Tool Input Models ============
class GradeInput(BaseModel):
    user_id: str = Field(description="用户 ID (学号)")
    term: str = Field(default="", description="学期，如 '2024-2025-1'，为空则查询全部")


class ScheduleInput(BaseModel):
    user_id: str = Field(description="用户 ID (学号)")
    term: str = Field(description="学期，如 '2024-2025-1'")
    week: str = Field(default="0", description="周次，'0' 为全部周")


class RankInput(BaseModel):
    user_id: str = Field(description="用户 ID (学号)")


class LevelExamInput(BaseModel):
    user_id: str = Field(description="用户 ID (学号)")


class SetPasswordInput(BaseModel):
    user_id: str = Field(description="用户 ID (学号)")
    password: str = Field(description="CAS 密码")


# ============ Tool Functions ============
def _get_jwc_service() -> JwcService:
    """获取 JwcService 实例"""
    return JwcService(get_session_manager())


def _format_grades(grades: list[Grade]) -> str:
    """格式化成绩为字符串"""
    if not grades:
        return "未查询到成绩记录"

    lines = ["## 成绩查询结果\n"]
    lines.append(f"| 学期 | 课程名称 | 成绩 | 学分 | 课程属性 | 课程性质 |")
    lines.append(f"|------|----------|------|------|----------|----------|")

    for g in grades:
        lines.append(f"| {g.term} | {g.course_name} | {g.score} | {g.credit} | {g.attribute} | {g.nature} |")

    return "\n".join(lines)


def _get_grades(user_id: str, term: str = "") -> str:
    """查询成绩"""
    try:
        service = _get_jwc_service()
        grades = service.get_grades(user_id, term)
        return _format_grades(grades)
    except Exception as e:
        logger.error(f"成绩查询失败: {e}")
        return f"成绩查询失败: {str(e)}"


def _format_schedule(classes: list[ClassEntry]) -> str:
    """格式化课表为字符串"""
    if not classes:
        return "未查询到课表记录"

    lines = ["## 课表查询结果\n"]
    lines.append(f"| 课程名称 | 教师 | 周次 | 地点 | 星期 | 节次 |")
    lines.append(f"|----------|------|------|------|------|------|")

    for c in classes:
        lines.append(f"| {c.course_name} | {c.teacher} | {c.weeks} | {c.place} | {c.day_of_week} | {c.time_of_day} |")

    return "\n".join(lines)


def _get_schedule(user_id: str, term: str, week: str = "0") -> str:
    """查询课表"""
    try:
        service = _get_jwc_service()
        classes = service.get_schedule(user_id, term, week)
        return _format_schedule(classes)
    except Exception as e:
        logger.error(f"课表查询失败: {e}")
        return f"课表查询失败: {str(e)}"


def _format_ranks(ranks: list[RankEntry]) -> str:
    """格式化排名为字符串"""
    if not ranks:
        return "未查询到排名记录"

    lines = ["## 专业排名结果\n"]
    lines.append(f"| 学期 | 总分 | 班级排名 | 平均分 |")
    lines.append(f"|------|------|----------|--------|")

    for r in ranks:
        lines.append(f"| {r.term} | {r.total_score} | {r.class_rank} | {r.average_score} |")

    return "\n".join(lines)


def _get_rank(user_id: str) -> str:
    """查询专业排名"""
    try:
        service = _get_jwc_service()
        ranks = service.get_rank(user_id)
        return _format_ranks(ranks)
    except Exception as e:
        logger.error(f"排名查询失败: {e}")
        return f"排名查询失败: {str(e)}"


def _format_level_exams(exams: list[LevelExamEntry]) -> str:
    """格式化等级考试为字符串"""
    if not exams:
        return "未查询到等级考试记录"

    lines = ["## 等级考试成绩\n"]
    lines.append(f"| 科目 | 笔试成绩 | 机试成绩 | 总分 | 笔试等级 | 机试等级 | 总等级 | 考试日期 |")
    lines.append(f"|------|----------|----------|------|----------|----------|--------|----------|")

    for e in exams:
        lines.append(f"| {e.course} | {e.written_score} | {e.computer_score} | {e.total_score} | {e.written_level} | {e.computer_level} | {e.total_level} | {e.exam_date} |")

    return "\n".join(lines)


def _get_level_exams(user_id: str) -> str:
    """查询等级考试成绩"""
    try:
        service = _get_jwc_service()
        exams = service.get_level_exams(user_id)
        return _format_level_exams(exams)
    except Exception as e:
        logger.error(f"等级考试查询失败: {e}")
        return f"等级考试查询失败: {str(e)}"


def _set_password(user_id: str, password: str) -> str:
    """设置用户 CAS 密码"""
    try:
        manager = get_session_manager()
        manager.set_password(user_id, password)
        return f"密码已成功保存，用户 {user_id} 可以使用教务系统功能了"
    except Exception as e:
        logger.error(f"密码保存失败: {e}")
        return f"密码保存失败: {str(e)}"


# ============ LangChain Tools ============
JwcGradeTool = StructuredTool.from_function(
    func=_get_grades,
    name="jwc_grade",
    description="查询学生的考试成绩。需要提供用户 ID（学号）和可选的学期参数。",
    args_schema=GradeInput,
)

JwcScheduleTool = StructuredTool.from_function(
    func=_get_schedule,
    name="jwc_schedule",
    description="查询学生的课表。需要提供用户 ID（学号）、学期和周次。",
    args_schema=ScheduleInput,
)

JwcRankTool = StructuredTool.from_function(
    func=_get_rank,
    name="jwc_rank",
    description="查询学生的专业排名。需要提供用户 ID（学号）。",
    args_schema=RankInput,
)

JwcLevelExamTool = StructuredTool.from_function(
    func=_get_level_exams,
    name="jwc_level_exam",
    description="查询学生的等级考试成绩（如英语四六级、计算机等级考试等）。需要提供用户 ID（学号）。",
    args_schema=LevelExamInput,
)

JwcSetPasswordTool = StructuredTool.from_function(
    func=_set_password,
    name="jwc_set_password",
    description="设置用户的 CAS 密码。首次使用教务系统功能前必须先设置密码。",
    args_schema=SetPasswordInput,
)


# 工具列表
JWC_TOOLS = [
    JwcGradeTool,
    JwcScheduleTool,
    JwcRankTool,
    JwcLevelExamTool,
    JwcSetPasswordTool,
]
```

- [ ] **Step 2: 更新 __init__.py**

```python
# backend/app/core/tools/jwc/__init__.py
from .client import Grade, ClassEntry, RankEntry, LevelExamEntry, JwcClient
from .service import JwcService
from .tools import (
    JwcGradeTool,
    JwcScheduleTool,
    JwcRankTool,
    JwcLevelExamTool,
    JwcSetPasswordTool,
    JWC_TOOLS,
    set_session_manager,
    get_session_manager,
)

__all__ = [
    "Grade",
    "ClassEntry",
    "RankEntry",
    "LevelExamEntry",
    "JwcClient",
    "JwcService",
    "JwcGradeTool",
    "JwcScheduleTool",
    "JwcRankTool",
    "JwcLevelExamTool",
    "JwcSetPasswordTool",
    "JWC_TOOLS",
    "set_session_manager",
    "get_session_manager",
]
```

- [ ] **Step 3: 提交代码**

```bash
cd backend
git add app/core/tools/jwc/tools.py app/core/tools/jwc/__init__.py
git commit -m "feat(jwc): add LangChain tools wrapper"
```

---

## Chunk 4: 集成与配置

### Task 4.1: 更新 config.py 添加配置

**Files:**
- Modify: `backend/app/config.py`

- [ ] **Step 1: 更新 config.py 添加 JWC 相关配置**

```python
# backend/app/config.py - 添加到 Settings 类

    # Session Storage
    session_storage_path: str = "./data/csu_sessions.json"
    password_storage_path: str = "./data/csu_passwords.json"
    password_encryption_key: str = "change-this-key-in-production"
    session_ttl_seconds: int = 30 * 60  # 30 minutes

    @classmethod
    def from_env(cls):
        return cls(
            # ... existing fields ...
            session_storage_path=os.getenv("SESSION_STORAGE_PATH", "./data/csu_sessions.json"),
            password_storage_path=os.getenv("PASSWORD_STORAGE_PATH", "./data/csu_passwords.json"),
            password_encryption_key=os.getenv("PASSWORD_ENCRYPTION_KEY", "change-this-key-in-production"),
            session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "1800")),
        )
```

- [ ] **Step 2: 提交代码**

```bash
cd backend
git add app/config.py
git commit -m "feat(config): add session and password storage settings"
```

---

### Task 4.2: 创建全局 SessionManager 实例

**Files:**
- Create: `backend/app/core/session/factory.py`

- [ ] **Step 1: 创建 factory.py**

```python
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
```

- [ ] **Step 2: 更新 session/__init__.py**

```python
# backend/app/core/session/__init__.py - 添加
from .factory import get_session_manager, create_session_manager, reset_session_manager

__all__ = [
    # ... existing exports ...
    "get_session_manager",
    "create_session_manager",
    "reset_session_manager",
]
```

- [ ] **Step 3: 更新 jwc/tools.py 使用 factory**

```python
# backend/app/core/tools/jwc/tools.py - 修改导入

# 替换:
# from app.core.session.manager import UnifiedSessionManager

# 为:
from app.core.session.factory import get_session_manager

def get_session_manager() -> UnifiedSessionManager:
    """获取全局 SessionManager"""
    return get_session_manager()
```

- [ ] **Step 4: 提交代码**

```bash
cd backend
git add app/core/session/factory.py app/core/session/__init__.py app/core/tools/jwc/tools.py
git commit -m "feat(session): add factory for global SessionManager"
```

---

### Task 4.3: 在 React Agent 中集成 JWC Tools

**Files:**
- Modify: `backend/app/core/agents/react_agent.py`

- [ ] **Step 1: 查看现有 React Agent 初始化方式**

```python
# backend/app/core/agents/react_agent.py - 检查 __init__ 方法

class ReactAgent:
    def __init__(
        self,
        model: BaseChatModel,
        system_prompt: Optional[str] = None,
        tools: List[BaseTool] = []
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.tools = tools
```

- [ ] **Step 2: 创建示例展示如何集成**

```python
# backend/app/core/agents/jwc_agent_example.py
"""
示例：如何在 React Agent 中集成 JWC Tools
"""
from langchain_openai import ChatOpenAI
from app.core.session.factory import get_session_manager
from app.core.tools.jwc import JWC_TOOLS

# 示例 1: 初始化时传入 JWC Tools
def create_jwc_agent():
    # 获取 SessionManager
    session_manager = get_session_manager()

    # 创建 LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    # 创建 Agent，传入 JWC Tools
    from app.core.agents.react_agent import ReactAgent

    system_prompt = """你是一个智能助手，可以帮助用户查询教务系统信息。

可用工具:
- jwc_grade: 查询成绩
- jwc_schedule: 查询课表
- jwc_rank: 查询专业排名
- jwc_level_exam: 查询等级考试成绩
- jwc_set_password: 设置密码（首次使用前必须调用）"""

    agent = ReactAgent(
        model=llm,
        system_prompt=system_prompt,
        tools=JWC_TOOLS  # 传入 JWC Tools
    )

    return agent
```

- [ ] **Step 3: 提交代码**

```bash
cd backend
git add app/core/agents/jwc_agent_example.py
git commit -m "docs: add example of integrating JWC tools with React Agent"
```

---

## Chunk 5: 最终集成测试

### Task 5.1: 集成测试

**Files:**
- Create: `backend/tests/core/test_jwc_integration.py`

- [ ] **Step 1: 编写集成测试**

```python
# backend/tests/core/test_jwc_integration.py
"""
集成测试：测试完整的 Session 获取和工具调用流程
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch

from app.core.session import (
    UnifiedSessionManager,
    SubsystemSessionCache,
    FileSessionPersistence,
    PasswordManager,
    LoginRateLimiter,
)
from app.core.tools.jwc import JwcService, set_session_manager
from app.core.tools.jwc.tools import (
    _get_grades,
    _get_schedule,
    _set_password,
    get_session_manager as get_jwc_session_manager,
)


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def session_manager(temp_dir):
    """创建 SessionManager 实例"""
    session_path = os.path.join(temp_dir, "sessions.json")
    password_path = os.path.join(temp_dir, "passwords.json")

    persistence = FileSessionPersistence(storage_path=session_path)
    password_mgr = PasswordManager(storage_path=password_path, encryption_key="test-key-12345")
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        password_manager=password_mgr,
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # 设置到全局
    set_session_manager(manager)

    return manager


def test_set_password_and_get(session_manager):
    """测试密码设置和获取"""
    session_manager.set_password("user1", "mypassword")

    password = session_manager.get_password("user1")
    assert password == "mypassword"


def test_session_manager_integration():
    """测试 SessionManager 集成"""
    manager = get_jwc_session_manager()
    assert manager is not None


@patch('app.core.tools.jwc.client.JwcClient.get_grades')
def test_jwc_service_get_grades(mock_get_grades, session_manager):
    """测试 JwcService.get_grades"""
    from app.core.tools.jwc.client import Grade

    # Mock 返回数据
    mock_get_grades.return_value = [
        Grade("2024-2025-1", "高等数学", "95", "4.0", "必修", "考试")
    ]

    service = JwcService(session_manager)
    grades = service.get_grades("user1")

    assert len(grades) == 1
    assert grades[0].course_name == "高等数学"
    assert grades[0].score == "95"


def test_tool_set_password(session_manager):
    """测试 JwcSetPasswordTool"""
    result = _set_password("user1", "testpassword")

    assert "成功" in result
    assert session_manager.get_password("user1") == "testpassword"


@patch('app.core.tools.jwc.client.JwcClient.get_grades')
def test_tool_get_grades(mock_get_grades, session_manager):
    """测试 JwcGradeTool"""
    from app.core.tools.jwc.client import Grade

    mock_get_grades.return_value = [
        Grade("2024-2025-1", "数据结构", "90", "3.0", "必修", "考试")
    ]

    result = _get_grades("user1", "2024-2025-1")

    assert "数据结构" in result
    assert "90" in result
```

- [ ] **Step 2: 运行集成测试**

Run: `cd backend && python -m pytest tests/core/test_jwc_integration.py -v`
Expected: PASS

- [ ] **Step 3: 提交代码**

```bash
cd backend
git add tests/core/test_jwc_integration.py
git commit -m "test: add integration tests for JWC tools"
```

---

## 总结

完成以上所有 Chunk 后，你将拥有：

1. **SessionManager 模块** - 完整的会话管理（缓存、持久化、密码、频率控制、CAS 登录）
2. **JwcService 模块** - 教务系统业务服务
3. **LangChain Tools** - 可直接用于 React Agent 的工具
4. **集成测试** - 验证完整流程

下一步可以将 JWC Tools 集成到实际的 React Agent 中使用。

---

**Plan complete and saved to `docs/superpowers/plans/2026-03-17-jwc-agent-integration-plan.md`. Ready to execute?**
