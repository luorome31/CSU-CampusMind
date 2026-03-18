# CAS 登录与会话管理重构设计

**日期**: 2026-03-18
**状态**: 已批准

## 背景

当前系统存在以下问题：

1. `/auth/login` 接口在登录时需要提供 subsystem 参数，这不合理
2. CAS 登录的核心 cookie `CASTGC` 没有被正确管理和复用
3. 不同子系统获取 session 的流程耦合在一起，缺乏可扩展性

## 目标

1. 简化登录接口：只需 username/password，获取 CASTGC 即算登录成功
2. 实现 CASTGC 用户级别缓存：跨子系统共享，TTL 约 2-4 小时
3. 子系统 session 获取策略模式：每个子系统实现自己的获取逻辑，支持自动注册

## 设计

### 1. 登录流程重构

**接口变化**：
- `POST /auth/login` 只接受 `username` 和 `password`
- 不再需要 `subsystem` 参数
- 登录成功获取 CASTGC 后直接返回 JWT

**流程**：
```
用户登录 → CAS 认证 → 获取 CASTGC → 缓存到用户级别 → 返回 JWT
```

### 2. CASTGC 缓存策略

- **存储位置**: UnifiedSessionManager 内存缓存
- **粒度**: 用户级别（user_id -> CASTGC）
- **TTL**: 2 小时（可配置）
- **作用**: 跨所有子系统共享，用于续期子系统 session

### 3. SubsystemSessionProvider 抽象

使用策略模式 + 自动注册机制：

```python
class SubsystemSessionProvider(ABC):
    """子系统 Session 获取策略基类（自动注册）"""

    _registry = {}  # subsystem_name -> Provider class

    def __init_subclass__(cls, subsystem_name: str = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if subsystem_name:
            cls._registry[subsystem_name] = cls

    @classmethod
    def get_provider(cls, subsystem_name: str) -> "SubsystemSessionProvider":
        """获取指定子系统的 session provider"""
        provider_class = cls._registry.get(subsystem_name)
        if not provider_class:
            raise ValueError(f"未找到子系统 {subsystem_name} 的处理策略")
        return provider_class()

    @abstractmethod
    def fetch_session(self, castgc: str) -> requests.Session:
        """核心抽象方法：输入 CASTGC，输出带着子系统有效凭证的 requests.Session"""
        pass
```

### 4. 具体子系统 Provider 实现

#### JWCSessionProvider (教务系统)

```python
class JWCSessionProvider(SubsystemSessionProvider, subsystem_name="jwc"):
    """教务系统：标准的 CAS 302 重定向流程"""

    SERVICE_URL = "http://csujwc.its.csu.edu.cn/sso.jsp"
    CAS_LOGIN_URL = "https://ca.csu.edu.cn/authserver/login"

    def fetch_session(self, castgc: str) -> requests.Session:
        session = requests.Session()
        session.headers.update(DEFAULT_HEADERS)

        # 1. 注入 CASTGC cookie
        session.cookies.set("CASTGC", castgc, domain="ca.csu.edu.cn")

        # 2. 访问 CAS 登录 URL with service，触发重定向到子系统
        login_url = f"{self.CAS_LOGIN_URL}?service={requests.utils.quote(self.SERVICE_URL)}"
        resp = session.get(login_url, allow_redirects=False)

        # 3. 跟随重定向到子系统，获取 JSESSIONID
        redirect_url = resp.headers.get("Location", "")
        if redirect_url:
            resp = session.get(redirect_url, allow_redirects=True)

        return session
```

#### LibrarySessionProvider (图书馆)

预留接口，后续实现。

### 5. UnifiedSessionManager 重构

```python
class UnifiedSessionManager:
    """
    统一会话管理器

    特性：
    1. CASTGC 用户级别缓存（跨子系统共享，TTL 2h）
    2. 子系统 Session 独立缓存（按 user_id + subsystem）
    3. 通过 SubsystemSessionProvider 获取子系统 session
    """

    def __init__(self, persistence, rate_limiter=None, ttl_seconds=30*60):
        self._cache = SubsystemSessionCache(ttl_seconds=ttl_seconds)
        self._persistence = persistence
        self._rate_limiter = rate_limiter or LoginRateLimiter()
        self._ttl = ttl_seconds
        # CASTGC 缓存：user_id -> {castgc, created_at, expires_at}
        self._castgc_cache: dict[str, dict] = {}

    def _get_castgc(self, user_id: str) -> Optional[str]:
        """获取缓存的 CASTGC"""

    def _save_castgc(self, user_id: str, castgc: str) -> None:
        """保存 CASTGC，TTL 2小时"""

    def get_session(self, user_id: str, subsystem: str) -> requests.Session:
        """
        获取指定子系统的会话

        流程：
        1. 检查子系统 session 缓存 → 存在且有效? → 直接返回
        2. 检查 CASTGC 缓存
        3. 若无 CASTGC，抛出异常（需要重新登录）
        4. 使用 SubsystemSessionProvider 获取子系统 session
        5. 缓存子系统 session
        """
```

### 6. Session 获取流程

```
ToolContext.get_subsystem_session(subsystem)
    │
    ├─► 检查 SubsystemSessionCache (user_id + subsystem)
    │       └─► 命中? → 返回缓存的 session
    │
    └─► 未命中
            │
            ├─► 获取 CASTGC (_castgc_cache)
            │       └─► 无 CASTGC? → 抛出 NeedReLoginError
            │
            └─► 获取 SubsystemSessionProvider(subsystem)
                    │
                    └─► provider.fetch_session(CASTGC)
                            │
                            └─► 返回带着 JSESSIONID 的 session
```

## 文件变更

| 操作 | 文件路径 | 说明 |
|------|----------|------|
| 新增 | `app/core/session/providers.py` | SubsystemSessionProvider 基类 |
| 新增 | `app/core/session/providers/jwc.py` | JWCSessionProvider |
| 新增 | `app/core/session/providers/library.py` | LibrarySessionProvider (预留) |
| 修改 | `app/core/session/manager.py` | 重构支持策略模式 |
| 修改 | `app/core/session/cas_login.py` | 简化只返回 CASTGC |
| 修改 | `app/api/v1/auth.py` | 简化登录接口 |

## 错误处理

| 错误 | 说明 | 处理 |
|------|------|------|
| `NeedReLoginError` | CASTGC 过期或不存在 | 前端引导用户重新登录 |
| `SubsystemNotSupportedError` | 子系统未注册 | 返回 400 错误 |
| `CASLoginError` | CAS 认证失败 | 返回 401 错误 |

## 测试策略

1. **单元测试**: 每个 Provider 独立测试
2. **集成测试**: 完整的登录 + session 获取流程
3. **Mock 测试**: 模拟 CAS 响应
