# 子系统集成指南：CAS Session Provider

**日期**: 2026-03-19
**状态**: 最佳实践指南

## 概述

本文档描述如何为 CampusMind 系统添加新的 CAS 子系统集成。

### 前置知识

添加新子系统前，请先阅读：
- [CAS Session 重构设计文档](./specs/2026-03-18-cas-session-refactor-design.md)
- `app/core/session/providers/` 目录下的现有实现

---

## 架构概览

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CAS 认证流程                                       │
│                                                                     │
│  ┌──────────┐     ┌──────────────┐     ┌───────────────┐          │
│  │ 用户登录  │ ──► │  CAS Server   │ ──► │   CASTGC      │          │
│  │ /auth    │     │  ca.csu.edu.cn│     │   (TGT)       │          │
│  └──────────┘     └──────────────┘     └───────────────┘          │
│                                                    │                │
│                                                    ▼                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                   SubsystemSessionProvider                     │ │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │ │
│  │  │  JWCProvider   │  │ LibraryProvider │  │ FutureXXX     │  │ │
│  │  │  (已实现)      │  │ (预留)          │  │ (按需添加)    │  │ │
│  │  └─────────────────┘  └─────────────────┘  └───────────────┘  │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│                              ▼                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐                    │
│  │   JWC      │  │  Library   │  │  Other     │                    │
│  │  Session   │  │  Session   │  │  Session   │                    │
│  └────────────┘  └────────────┘  └────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 添加新子系统的步骤

### Step 1: 分析目标子系统

在开始实现之前，你需要了解：

1. **CAS Service URL**: 子系统在 CAS 中的 service URL
2. **Session 获取流程**: 通过 CASTGC 获取子系统 session 的具体流程
3. **Session Cookie 名称**: 子系统使用的 cookie 名称（如 `JSESSIONID`）

#### 如何分析

1. 打开浏览器开发者工具
2. 访问 CAS 登录页面: `https://ca.csu.edu.cn/authserver/login?service=<目标子系统URL>`
3. 观察网络请求，特别是：
   - 302 重定向的目标地址
   - 最终设置的 cookies

### Step 2: 创建 Provider 类

在 `app/core/session/providers/` 目录下创建新的 provider 文件。

**文件命名规范**: `<子系统名>.py`（如 `library.py`）

**代码模板**:

```python
# app/core/session/providers/<subsystem>.py
import logging
import requests
from urllib.parse import urljoin

from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session import cas_login

logger = logging.getLogger(__name__)


class XxxSessionProvider(SubsystemSessionProvider, subsystem_name="xxx"):
    """
    XXX 系统 Session Provider

    描述子系统的特点和处理逻辑
    """

    # 子系统的 CAS service URL
    SERVICE_URL = "https://xxx.csu.edu.cn/..."

    # CAS 登录 URL（固定不变）
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"

    def fetch_session(self, castgc: str) -> requests.Session:
        """
        使用 CASTGC 获取子系统 session

        流程:
        1. 创建新 session，设置 CASTGC cookie
        2. 访问 CAS login URL with service
        3. 处理重定向，获取子系统 cookie
        """
        session = cas_login.create_session()

        # 1. 注入 CASTGC cookie
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # 2. 访问 CAS 登录 URL with service
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        logger.info(f"XXX: Using CASTGC to access {login_url}")

        resp = session.get(login_url, allow_redirects=False)

        # 3. 处理重定向（根据实际情况调整）
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            if not redirect_url.startswith("http"):
                redirect_url = urljoin(login_url, redirect_url)
            resp = session.get(redirect_url, allow_redirects=True)
            logger.info(f"XXX: Subsystem final URL: {resp.url}")

        return session
```

### Step 3: 更新 providers/__init__.py

```python
# app/core/session/providers/__init__.py
from app.core.session.providers.base import SubsystemSessionProvider
from app.core.session.providers.jwc import JWCSessionProvider
from app.core.session.providers.xxx import XxxSessionProvider  # 新增

__all__ = [
    "SubsystemSessionProvider",
    "JWCSessionProvider",
    "XxxSessionProvider",  # 新增
]
```

### Step 4: 更新 Subsystem 常量（如需要）

在 `app/core/session/manager.py` 中添加子系统标识：

```python
class Subsystem:
    """子系统标识"""
    JWC = "jwc"
    LIBRARY = "library"
    # 新增
    XXX = "xxx"
```

### Step 5: 编写单元测试

```python
# tests/core/session/test_providers_xxx.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.session.providers.xxx import XxxSessionProvider


class TestXxxSessionProvider:
    """测试 XxxSessionProvider"""

    def test_provider_registered(self):
        """Provider 应自动注册"""
        from app.core.session.providers.base import SubsystemSessionProvider
        assert "xxx" in SubsystemSessionProvider._registry

    def test_fetch_session_sets_castgc(self):
        """fetch_session 应设置 CASTGC cookie"""
        with patch("app.core.session.providers.xxx.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.cookies.set = Mock()
            mock_session.get = Mock()
            mock_session.headers = {}
            mock_create.return_value = mock_session

            provider = XxxSessionProvider()
            provider.fetch_session("test_castgc_value")

            mock_session.cookies.set.assert_called_once_with(
                "CASTGC", "test_castgc_value", domain="ca.csu.edu.cn"
            )

    def test_fetch_session_returns_session(self):
        """fetch_session 应返回 session 对象"""
        with patch("app.core.session.providers.xxx.cas_login.create_session") as mock_create:
            mock_session = MagicMock()
            mock_session.get = Mock(return_value=MagicMock(
                headers={"Location": ""},
                url="https://xxx.csu.edu.cn/"
            ))
            mock_session.cookies.set = Mock()
            mock_create.return_value = mock_session

            provider = XxxSessionProvider()
            result = provider.fetch_session("test_castgc")

            assert result == mock_session
```

### Step 6: 集成测试

```python
# tests/core/session/test_integration.py（添加新测试）

def test_xxx_provider_auto_registration(self):
    """测试 XXX Provider 自动注册"""
    from app.core.session.providers.base import SubsystemSessionProvider
    from app.core.session.providers.xxx import XxxSessionProvider

    assert "xxx" in SubsystemSessionProvider._registry
    provider = SubsystemSessionProvider.get_provider("xxx")
    assert isinstance(provider, XxxSessionProvider)
```

---

## 不同获取流程的 Provider 示例

### 模式 A: 标准 CAS 302 重定向

适用于大多数标准 CAS 子系统（如 JWC）：

```python
class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
    SERVICE_URL = "http://csujwc.its.csu.edu.cn/sso.jsp"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        resp = session.get(login_url, allow_redirects=False)

        # 跟随重定向
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            resp = session.get(redirect_url, allow_redirects=True)

        return session
```

### 模式 B: 需要二次请求

适用于某些特殊子系统，需要额外步骤：

```python
class LibrarySessionProvider(SubsystemSessionProvider, subsystem_name="library"):
    SERVICE_URL = "https://lib.csu.edu.cn/system/resource/code/auth/clogin.jsp"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # Step 1: CAS 重定向
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        resp = session.get(login_url, allow_redirects=False)

        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            # Step 2: 访问子系统获取临时 token
            resp = session.get(redirect_url, allow_redirects=False)
            temp_token = resp.cookies.get("temp_token")

            # Step 3: 用临时 token 换取正式 session
            if temp_token:
                final_resp = session.post(
                    "https://lib.csu.edu.cn/api/exchange",
                    data={"temp_token": temp_token}
                )

        return session
```

### 模式 C: API Token 模式

适用于提供 REST API 的子系统：

```python
class ApiSessionProvider(SubsystemSessionProvider, subsystem_name="api"):
    SERVICE_URL = "https://api.csu.edu.cn/cas"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = cas_login.create_session()
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # CAS 重定向获取子系统 session
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        resp = session.get(login_url, allow_redirects=True)

        # 子系统可能返回 API token
        api_token = resp.cookies.get("api_token")
        if api_token:
            session.headers.update({"Authorization": f"Bearer {api_token}"})

        return session
```

---

## 文件清单

添加新子系统需要修改/创建的文件：

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| **创建** | `app/core/session/providers/<xxx>.py` | 新子系统 Provider |
| **修改** | `app/core/session/providers/__init__.py` | 导出新 Provider |
| **可选** | `app/core/session/manager.py` | 添加 Subsystem 常量 |
| **创建** | `tests/core/session/test_providers_<xxx>.py` | Provider 单元测试 |
| **修改** | `tests/core/session/test_integration.py` | 添加集成测试 |

---

## 测试验证

### 1. 本地 Mock 测试

```bash
cd /home/luorome/software/CampusMind/backend
uv run pytest tests/core/session/test_providers_<xxx>.py -v
```

### 2. 集成测试

```bash
uv run pytest tests/core/session/test_integration.py -v
```

### 3. 真实环境测试

```python
# 使用真实账号测试
import os
from dotenv import load_dotenv
load_dotenv()

from app.core.session import cas_login
from app.core.session.providers.xxx import XxxSessionProvider

# 1. 登录获取 CASTGC
castgc = cas_login.cas_login_only_castgc(
    os.getenv("CAS_USERNAME"),
    os.getenv("CAS_PASSWORD")
)

# 2. 获取子系统 session
provider = XxxSessionProvider()
session = provider.fetch_session(castgc)

print(f"Cookies: {[c.name for c in session.cookies]}")
```

### 4. API 端到端测试

```bash
# 启动服务器
uv run uvicorn app.main:app --host 127.0.0.1 --port 18000

# 测试登录
curl -X POST http://127.0.0.1:18000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "你的学号", "password": "你的密码"}'
```

---

## 常见问题

### Q: Provider 没有自动注册？

检查：
1. `subsystem_name` 参数是否正确传递
2. 类定义时是否使用了 `class XxxProvider(SubsystemSessionProvider, subsystem_name="xxx"):`
3. 模块是否被正确导入

### Q: 获取 session 失败？

1. 确认 CASTGC 有效（未过期）
2. 检查 SERVICE_URL 是否正确
3. 查看日志中的重定向地址
4. 确认子系统是否需要额外的认证步骤

### Q: 如何调试？

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 参考实现

- [JWCSessionProvider](app/core/session/providers/jwc.py) - 标准 CAS 重定向模式
