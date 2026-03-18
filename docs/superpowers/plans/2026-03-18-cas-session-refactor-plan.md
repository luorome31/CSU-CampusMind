# CAS Session 重构实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构 CAS 登录与会话管理系统，实现策略模式支持多子系统自动注册

**Architecture:**
- 使用 SubsystemSessionProvider 抽象基类 + 自动注册机制
- CASTGC 用户级别缓存，跨子系统共享
- UnifiedSessionManager 协调 CASTGC 和各子系统 Provider

**Tech Stack:** Python, requests, FastAPI, pytest
**Dependency Manager:** uv

---

## Chunk 1: SubsystemSessionProvider 抽象基类

**Files:**
- Create: `backend/app/core/session/providers/__init__.py`
- Create: `backend/app/core/session/providers/base.py`
- Test: `backend/tests/core/session/test_providers.py`

- [ ] **Step 1: 创建 providers 目录和 __init__.py**

```python
# backend/app/core/session/providers/__init__.py
from app.core.session.providers.base import SubsystemSessionProvider

__all__ = ["SubsystemSessionProvider"]
```

- [ ] **Step 2: 创建 base.py - Provider 抽象基类**

```python
# backend/app/core/session/providers/base.py
from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Type
import requests


class SubsystemSessionProvider(ABC):
    """
    子系统 Session 获取策略基类（自动注册）

    使用方式:
    class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
        def fetch_session(self, castgc: str) -> requests.Session:
            ...
    """

    _registry: ClassVar[Dict[str, Type["SubsystemSessionProvider"]]] = {}

    def __init_subclass__(cls, subsystem_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if subsystem_name:
            cls._registry[subsystem_name] = cls

    @classmethod
    def get_provider(cls, subsystem_name: str) -> "SubsystemSessionProvider":
        """获取指定子系统的 session provider"""
        provider_class = cls._registry.get(subsystem_name)
        if not provider_class:
            raise ValueError(f"未找到子系统 {subsystem_name} 的处理策略，请检查是否已注册")
        return provider_class()

    @classmethod
    def list_registered_providers(cls) -> list:
        """列出所有已注册的子系统"""
        return list(cls._registry.keys())

    @abstractmethod
    def fetch_session(self, castgc: str) -> requests.Session:
        """
        核心抽象方法：输入 CASTGC，输出带着子系统有效凭证的 requests.Session

        Args:
            castgc: CAS 登录成功后获取的 CASTGC cookie

        Returns:
            带着子系统有效 session 的 requests.Session
        """
        pass
```

- [ ] **Step 3: 编写测试**

```python
# backend/tests/core/session/test_providers.py
import pytest
from unittest.mock import Mock, MagicMock
from app.core.session.providers.base import SubsystemSessionProvider


class TestSubsystemSessionProvider:
    """测试 SubsystemSessionProvider 基类"""

    def test_registry_starts_empty(self):
        """注册表初始为空"""
        # 创建一个临时子类验证注册机制
        class DummyProvider(SubsystemSessionProvider, subsystem_name="dummy"):
            def fetch_session(self, castgc):
                return Mock()

        assert "dummy" in SubsystemSessionProvider._registry
        provider = SubsystemSessionProvider.get_provider("dummy")
        assert isinstance(provider, DummyProvider)

    def test_get_unknown_provider_raises(self):
        """获取未注册的 provider 抛出异常"""
        with pytest.raises(ValueError) as exc_info:
            SubsystemSessionProvider.get_provider("unknown")
        assert "unknown" in str(exc_info.value)

    def test_list_registered_providers(self):
        """列出已注册的 providers"""
        class AnotherProvider(SubsystemSessionProvider, subsystem_name="another"):
            def fetch_session(self, castgc):
                return Mock()

        providers = SubsystemSessionProvider.list_registered_providers()
        assert "dummy" in providers
        assert "another" in providers
```

- [ ] **Step 4: 运行测试验证**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_providers.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: 提交**

```bash
git add backend/app/core/session/providers/ backend/tests/core/session/test_providers.py
git commit -m "feat(session): add SubsystemSessionProvider base class with auto-registration"
```

---

## Chunk 2: JWCSessionProvider 实现

**Files:**
- Create: `backend/app/core/session/providers/jwc.py`
- Modify: `backend/app/core/session/providers/__init__.py`
- Test: `backend/tests/core/session/test_providers_jwc.py`

- [ ] **Step 1: 创建 JWC Provider 实现**

```python
# backend/app/core/session/providers/jwc.py
import logging
import requests
from urllib.parse import urljoin

from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session import cas_login

logger = logging.getLogger(__name__)


class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
    """
    教务系统 Session Provider

    流程:
    1. 创建新 session，设置 CASTGC cookie
    2. 访问 CAS login URL with service，触发重定向到 JWC
    3. 跟随重定向，获取 JWC 的 JSESSIONID
    """

    SERVICE_URL = "http://csujwc.its.csu.edu.cn/sso.jsp"
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()

        # 1. 注入 CASTGC cookie
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # 2. 访问 CAS 登录 URL with service，触发重定向到 JWC
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        logger.info(f"JWC: Using CASTGC to access {login_url}")

        resp = session.get(login_url, allow_redirects=False)

        # 3. 跟随重定向到 JWC，获取 JSESSIONID
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)
            resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"JWC: Subsystem final URL: {resp.url}")

        return session
```

- [ ] **Step 2: 更新 __init__.py 导出**

```python
# backend/app/core/session/providers/__init__.py
from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session.providers.jwc import JWCSessionProvider

__all__ = ["SubsystemSessionProvider", "JWCSessionProvider"]
```

- [ ] **Step 3: 编写测试**

```python
# backend/tests/core/session/test_providers_jwc.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.session.providers.jwc import JWCSessionProvider


class TestJWCSessionProvider:
    """测试 JWCSessionProvider"""

    def test_provider_registered(self):
        """JWC Provider 已自动注册"""
        from app.core.session.providers.base import SubsystemSessionProvider
        assert "jwc" in SubsystemSessionProvider._registry

    def test_fetch_session_sets_castgc(self):
        """fetch_session 应设置 CASTGC cookie"""
        with patch("app.core.session.providers.jwc.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock()
            mock_session.headers = {}
            mock_create.return_value = mock_session

            provider = JWCSessionProvider()
            provider.fetch_session("test_castgc_value")

            mock_session.cookies.set.assert_called_once_with(
                "CASTGC", "test_castgc_value", domain="ca.csu.edu.cn"
            )

    def test_fetch_session_returns_session(self):
        """fetch_session 应返回 session 对象"""
        with patch("app.core.session.providers.jwc.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={"Location": ""},
                url="http://csujwc.its.csu.edu.cn/"
            ))
            mock_session.cookies.set = Mock()
            mock_create.return_value = mock_session

            provider = JWCSessionProvider()
            result = provider.fetch_session("test_castgc")

            assert result == mock_session
```

- [ ] **Step 4: 运行测试验证**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_providers_jwc.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: 提交**

```bash
git add backend/app/core/session/providers/jwc.py backend/tests/core/session/test_providers_jwc.py
git commit -m "feat(session): add JWCSessionProvider with CASTGC-based auth"
```

---

## Chunk 3: UnifiedSessionManager 重构

**Files:**
- Modify: `backend/app/core/session/manager.py`
- Test: `backend/tests/core/session/test_manager.py`

- [ ] **Step 1: 修改 manager.py 引入 Provider**

在文件开头添加导入：
```python
from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session.providers.jwc import JWCSessionProvider
```

- [ ] **Step 2: 重构 get_session 方法**

替换现有的 `_get_session_with_castgc` 和 `get_session` 方法：

```python
def _get_castgc(self, user_id: str) -> Optional[str]:
    """获取缓存的 CASTGC cookie"""
    if user_id not in self._castgc_cache:
        return None

    castgc_data = self._castgc_cache[user_id]
    import time
    if time.time() > castgc_data.get("expires_at", 0):
        del self._castgc_cache[user_id]
        return None

    return castgc_data.get("castgc")

def _save_castgc(self, user_id: str, castgc: str) -> None:
    """保存 CASTGC cookie，TTL 2小时"""
    import time
    self._castgc_cache[user_id] = {
        "castgc": castgc,
        "created_at": time.time(),
        "expires_at": time.time() + 2 * 3600,
    }

def get_session(self, user_id: str, subsystem: str) -> requests.Session:
    """
    获取指定子系统的会话

    流程：
    1. 检查子系统 session 缓存 → 存在且有效? → 直接返回
    2. 检查 CASTGC
    3. 若无 CASTGC，抛出 NeedReLoginError
    4. 使用 SubsystemSessionProvider 获取子系统 session
    5. 缓存子系统 session
    """
    # 1. 检查子系统 session 缓存
    cached = self._cache.get(user_id, subsystem)
    if cached:
        logger.info(f"Using cached session for {user_id}:{subsystem}")
        return cached.session

    # 2. 检查持久化缓存
    loaded_session = self._persistence.load(user_id, subsystem)
    if loaded_session:
        self._cache.set(user_id, subsystem, loaded_session)
        logger.info(f"Loaded session from persistence for {user_id}:{subsystem}")
        return loaded_session

    # 3. 获取 CASTGC
    castgc = self._get_castgc(user_id)
    if not castgc:
        raise NeedReLoginError(
            f"用户 {user_id} 的 CASTGC 已过期或不存在，请重新登录"
        )

    # 4. 使用 Provider 获取子系统 session
    provider = SubsystemSessionProvider.get_provider(subsystem)
    session = provider.fetch_session(castgc)

    # 5. 缓存
    self._cache.set(user_id, subsystem, session)
    self._persistence.save(user_id, subsystem, session, self._ttl)

    logger.info(f"Fetched new session for {user_id}:{subsystem}")
    return session
```

- [ ] **Step 3: 添加 NeedReLoginError 异常类**

在 manager.py 顶部添加：
```python
class NeedReLoginError(Exception):
    """需要重新登录错误（CASTGC 过期或不存在）"""
    pass
```

- [ ] **Step 4: 修改 get_session 移除 service_url 参数**

原来的 `cas_login.cas_login(username, password, service_url, rate_limiter)` 调用需要修改为只获取 CASTGC。

创建新的简化登录函数 `cas_login_only_castgc`：
```python
def cas_login_only_castgc(username: str, password: str, rate_limiter=None) -> str:
    """
    仅获取 CASTGC，不访问任何子系统

    Returns:
        CASTGC cookie 值
    """
    if rate_limiter:
        if not rate_limiter.can_login(username):
            wait_time = rate_limiter.get_wait_time(username)
            raise AccountLockedError(f"登录过于频繁，请等待 {wait_time:.0f} 秒后再试")
        rate_limiter.record_login(username)

    session = create_session()

    try:
        # 任选一个 service_url，只需要能获取 CASTGC
        service_url = SUBSYSTEM_SERVICE_URLS.get("jwc")
        login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"

        resp = session.get(login_url, allow_redirects=False)
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]
        event_id = soup.find("input", {"name": "_eventId"})["value"]
        dllt = soup.find("input", {"name": "dllt"})["value"]
        salt = soup.find("input", {"id": "pwdEncryptSalt"})["value"]

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

        resp = session.post(login_url, data=form_data, allow_redirects=False)

        cookies = {c.name: c.value for c in session.cookies}
        castgc = cookies.get("CASTGC")

        if not castgc:
            if "密码" in resp.text or "错误" in resp.text:
                raise CASLoginError("用户名或密码错误")
            raise CASLoginError(f"登录失败: 未获取到 CASTGC")

        return castgc

    except AccountLockedError:
        raise
    except requests.RequestException as e:
        raise CASLoginError(f"网络请求失败: {e}")
```

- [ ] **Step 5: 更新 manager.py 的 login 方法**

在 manager.py 中添加 `login` 方法来获取和保存 CASTGC：
```python
def login(self, user_id: str, username: str, password: str) -> None:
    """
    用户登录 CAS，获取 CASTGC

    Args:
        user_id: 用户 ID (通常是 username)
        username: CAS 用户名
        password: CAS 密码
    """
    castgc = cas_login_only_castgc(username, password, self._rate_limiter)
    self._save_castgc(user_id, castgc)
    logger.info(f"User {user_id} logged in, CASTGC saved")
```

- [ ] **Step 6: 编写/更新测试**

```python
# backend/tests/core/session/test_manager.py 新增测试
def test_get_session_uses_provider():
    """get_session 应使用 SubsystemSessionProvider"""
    # ... mock cache miss, persistence miss, then verify provider is called
    pass

def test_get_session_raises_when_no_castgc():
    """无 CASTGC 时应抛出 NeedReLoginError"""
    # ... mock cache and persistence miss, verify NeedReLoginError
    pass
```

- [ ] **Step 7: 运行测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_manager.py -v`

- [ ] **Step 8: 提交**

```bash
git add backend/app/core/session/manager.py backend/tests/core/session/test_manager.py
git commit -m "refactor(session): integrate SubsystemSessionProvider into UnifiedSessionManager"
```

---

## Chunk 4: 简化 /auth/login 接口

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Test: `backend/tests/api/test_auth.py`

- [ ] **Step 1: 修改 LoginRequest 模型**

移除 `subsystem` 字段：
```python
class LoginRequest(BaseModel):
    username: str  # 学号
    password: str
```

- [ ] **Step 2: 修改 login 接口实现**

```python
@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    用户登录接口

    流程：
    1. 检查登录频率
    2. 调用 CAS 登录获取 CASTGC
    3. 存储 CASTGC 到 session manager
    4. 生成 JWT 返回
    """
    # 1. 登录频率检查
    try:
        _rate_limiter.check(request.username)
    except Exception as e:
        logger.warning(f"Login rate limit exceeded for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"登录过于频繁，请稍后再试: {str(e)}"
        )

    # 2. 获取 session manager
    session_manager = get_session_manager()

    # 3. CAS 登录获取 CASTGC
    try:
        from app.core.session.manager import NeedReLoginError

        session_manager.login(
            user_id=request.username,
            username=request.username,
            password=request.password
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )
    except CASLoginError as e:
        logger.error(f"CAS login failed for {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"登录失败: {str(e)}"
        )

    # 4. 生成 JWT
    token = jwt_manager.create_token({"user_id": request.username})

    logger.info(f"User {request.username} logged in successfully")

    return LoginResponse(
        token=token,
        user_id=request.username,
        expires_in=settings.jwt_expire_hours * 3600
    )
```

- [ ] **Step 3: 验证语法**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.api.v1.auth import router; print('Auth router OK')"`

- [ ] **Step 4: 提交**

```bash
git add backend/app/api/v1/auth.py
git commit -m "refactor(auth): simplify login to only require username/password"
```

---

## Chunk 5: 整体集成测试

**Files:**
- Create: `backend/tests/core/session/test_integration.py`

- [ ] **Step 1: 编写集成测试**

```python
"""
完整登录流程集成测试

测试场景:
1. 用户登录获取 CASTGC
2. 使用 CASTGC 通过 Provider 获取子系统 session
3. 验证 session 可以访问子系统
"""

def test_full_login_flow_mock():
    """完整流程测试（Mock CAS）"""
    from unittest.mock import patch, MagicMock

    with patch("app.core.session.cas_login.create_session") as mock_create:
        mock_session = MagicMock()
        mock_session.cookies.set = MagicMock()
        mock_session.get = MagicMock(return_value=MagicMock(
            headers={"Location": "http://csujwc.its.csu.edu.cn/"},
            text="<html>JWC System</html>"
        ))
        mock_create.return_value = mock_session

        # 1. 登录获取 CASTGC
        from app.core.session.manager import UnifiedSessionManager
        from app.core.session.providers.jwc import JWCSessionProvider

        # ... 完成测试
```

- [ ] **Step 2: 运行集成测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_integration.py -v`

- [ ] **Step 3: 提交**

```bash
git add backend/tests/core/session/test_integration.py
git commit -m "test(session): add full login flow integration test"
```

---

## 执行顺序

1. Chunk 1: SubsystemSessionProvider 抽象基类
2. Chunk 2: JWCSessionProvider 实现
3. Chunk 3: UnifiedSessionManager 重构
4. Chunk 4: 简化 /auth/login 接口
5. Chunk 5: 整体集成测试

每个 Chunk 完成后进行 Review，Review 通过后进入下一个 Chunk。
