# 教务系统工具集成设计文档

**日期**: 2026-03-17
**主题**: 在 LangGraph React Agent 中接入教务系统业务查询工具

## 一、项目概述

### 1.1 目标

在现有 LangGraph React Agent 中接入教务系统（JWC）业务查询功能，实现多用户环境下的 Session 管理和业务数据查询。

### 1.2 核心需求

- **多用户系统**: 按用户 ID 隔离各用户的 Session
- **混合认证模式**:
  - 用户 ID 已知
  - 首次访问某子系统时需要 CAS 登录获取该子系统的 Session
  - Session 失效前可复用
- **子系统独立**: 各子系统（教务、图书馆、校园卡等）Session 独立管理
- **存储方式**: 文件存储，预留 Redis 接口

### 1.3 参考实现

- 文档: `/home/luorome/software/CampusMind/reference_doc/SESSION_DEVELOPMENT_SUMMARY.md`
- 代码: `/home/luorome/software/CampusMind/scripts/csu_system_scripts/`

---

## 二、架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   React Agent                        │
│  tools: [JwcGradeTool, JwcScheduleTool, ...]       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│              JwcService (业务层)                     │
│  - 使用 SessionManager 获取 Session                  │
│  - 调用各业务方法                                      │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│         SessionManager (会话管理层)                   │
│  - 用户+子系统粒度缓存                                 │
│  - CAS 登录（密码加密存储）                            │
│  - 持久化（文件/Redis）                                │
└─────────────────────────────────────────────────────┘
```

### 2.2 设计原则

采用**方案 B（中等耦合）**:
- Session 管理与业务逻辑分离
- 分层清晰，便于测试和维护
- 预留 Redis 扩展接口

---

## 三、模块设计

### 3.1 SessionManager 模块

#### 3.1.1 SubsystemSessionCache

内存缓存，按 `user_id:subsystem` 粒度存储。

```python
class SubsystemSessionCache:
    def __init__(self, ttl_seconds: int = 30 * 60)
    def get(self, user_id: str, subsystem: str) -> Optional[CachedSession]
    def set(self, user_id: str, subsystem: str, session: requests.Session) -> None
    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None
```

#### 3.1.2 LoginRateLimiter

登录频率控制，防止账号被封。

```python
class LoginRateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 300)
    def can_login(self, user_id: str) -> bool
    def record_login(self, user_id: str) -> None
    def get_wait_time(self, user_id: str) -> float
```

#### 3.1.3 SessionPersistence

Session 持久化（文件/Redis）。

```python
class SessionPersistence(ABC):
    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None
    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]
    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None

class FileSessionPersistence(SessionPersistence):
    def __init__(self, storage_path: str)

class RedisSessionPersistence(SessionPersistence):  # 预留
    def __init__(self, redis_url: str)
```

#### 3.1.4 PasswordManager

CAS 密码加密存储。

```python
class PasswordManager:
    def __init__(self, storage_path: str, encryption_key: str)
    def save_password(self, user_id: str, password: str) -> None
    def get_password(self, user_id: str) -> Optional[str]
    def delete_password(self, user_id: str) -> None
```

#### 3.1.5 UnifiedSessionManager

统一会话管理器。

```python
class UnifiedSessionManager:
    def __init__(
        self,
        password_manager: PasswordManager,
        persistence: SessionPersistence,
        rate_limiter: Optional[LoginRateLimiter] = None,
        ttl_seconds: int = 30 * 60
    )

    def set_password(self, user_id: str, password: str) -> None:
        """存储用户 CAS 密码"""

    def get_session(self, user_id: str, subsystem: str) -> requests.Session:
        """自动获取 Session（自动登录/复用）"""

    def invalidate_session(self, user_id: str, subsystem: Optional[str] = None) -> None:
        """使会话失效"""
```

### 3.2 JwcService 模块

#### 3.2.1 JwcClient

教务系统业务客户端。

```python
class Grade:
    term: str
    course_name: str
    score: str
    credit: str
    attribute: str
    nature: str

class ClassEntry:
    course_name: str
    teacher: str
    weeks: str
    place: str
    day_of_week: str
    time_of_day: str

class JwcClient:
    def __init__(self, session: requests.Session)
    def get_grades(self, term: str = "") -> list[Grade]
    def get_rank(self) -> list[RankEntry]
    def get_class_schedule(self, term: str, week: str = "0") -> list[ClassEntry]
    def get_level_exams(self) -> list[LevelExamEntry]
```

#### 3.2.2 JwcService

教务系统服务入口。

```python
class JwcService:
    def __init__(self, session_manager: UnifiedSessionManager)
    def get_grades(self, user_id: str, term: str = "") -> list[Grade]
    def get_schedule(self, user_id: str, term: str, week: str = "0") -> list[ClassEntry]
    # ...
```

### 3.3 LangChain Tools

将业务方法封装为 LangChain BaseTool。

```python
from langchain_core.tools import BaseTool

class JwcGradeTool(BaseTool):
    name: str = "jwc_grade"
    description: str = "查询学生成绩"

    def _run(self, user_id: str, term: str = "") -> str:
        ...

class JwcScheduleTool(BaseTool):
    name: str = "jwc_schedule"
    description: str = "查询课表"

    def _run(self, user_id: str, term: str, week: str = "0") -> str:
        ...

# 更多工具...
```

---

## 四、数据流

### 4.1 首次访问流程

```
用户首次调用 Agent（如查成绩）
    │
    ▼
Tool (JwcGradeTool)
    │
    ├── 调用 JwcService.get_grades(user_id)
    │
    ▼
JwcService
    │
    ├── 调用 SessionManager.get_session(user_id, "jwc")
    │
    ▼
SessionManager
    │
    ├── 检查内存缓存 → 无
    ├── 检查文件缓存 → 无
    │
    ├── 从 PasswordManager 获取密码
    │       └── 无密码 → 抛出异常 "需要先设置密码"
    │
    ├── CAS 登录 → 获取 JWC Session
    │       └── 频率控制检查
    │
    ├── 缓存到内存
    ├── 持久化到文件
    │
    ▼
返回 Session
    │
    ▼
JwcClient.get_grades() 执行查询
    │
    ▼
返回结果给 Agent
```

### 4.2 后续访问流程

```
用户再次调用 Agent（Session 未过期）
    │
    ▼
SessionManager.get_session(user_id, "jwc")
    │
    ├── 检查内存缓存 → 有则直接返回
    │       └── 返回 Session
    │
    ▼
JwcClient.get_grades() 执行查询
    │
    ▼
返回结果
```

---

## 五、文件结构

```
backend/app/
├── core/
│   ├── session/              # 新增：会话管理模块
│   │   ├── __init__.py
│   │   ├── manager.py        # UnifiedSessionManager
│   │   ├── cache.py          # SubsystemSessionCache
│   │   ├── persistence.py    # SessionPersistence (文件/Redis)
│   │   ├── rate_limiter.py   # LoginRateLimiter
│   │   ├── password.py       # PasswordManager
│   │   └── cas_login.py      # CAS 登录逻辑
│   │
│   ├── tools/
│   │   ├── jwc/              # 新增：教务系统工具
│   │   │   ├── __init__.py
│   │   │   ├── service.py   # JwcService
│   │   │   ├── client.py     # JwcClient + 数据模型
│   │   │   └── tools.py      # LangChain Tools 封装
│   │   │
│   │   └── ... (现有工具)
│   │
│   └── agents/
│       └── react_agent.py    # 现有 React Agent
│
├── config.py                 # 配置（存储路径等）
```

---

## 六、错误处理

| 场景 | 处理方式 |
|------|----------|
| 用户未设置密码 | 抛出异常，提示用户先通过 `set_password` 设置密码 |
| 登录频率超限 | 抛出异常，提示等待时间 |
| CAS 登录失败 | 抛出异常，记录错误日志 |
| Session 失效 | 自动重新登录（调用 CAS） |
| 业务查询失败 | 返回错误信息给 Agent |

---

## 七、测试策略

### 7.1 单元测试

- SessionManager 各组件独立测试
- PasswordManager 加解密测试
- JwcClient 业务解析测试

### 7.2 集成测试

- 模拟完整登录流程
- Session 缓存与持久化测试

### 7.3 E2E 测试

- React Agent 集成测试（需要真实 CAS 环境或 Mock）

---

## 八、后续扩展

1. **添加 Redis 支持**: 实现 `RedisSessionPersistence` 接口
2. **添加其他子系统**: 图书馆、校园卡（参考 JWC 实现）
3. **添加监控告警**: 登录失败告警

---

## 九、关键参考

- CAS 认证关键点: 见 `SESSION_DEVELOPMENT_SUMMARY.md`
- Session 复用原理: 用户+子系统粒度缓存
- 登录频率控制: 5 分钟内最多 5 次

---

**审批状态**: 已批准
**创建时间**: 2026-03-17
