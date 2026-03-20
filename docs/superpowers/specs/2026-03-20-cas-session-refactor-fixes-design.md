# CAS Session Refactor — Bug Fixes

**日期**: 2026-03-20
**状态**: Draft
**PR 范围**: Single PR for all 5 tasks

## 背景

2026-03-18 的 CAS Session 重构设计已批准实施。在代码审查和自测过程中发现 5 个需要修复的问题，集中在 `cas_login.py`、`manager.py`、`persistence.py`、`redis_persistence.py` 和 `password.py` 五个文件中。

## 问题列表

| # | 问题 | 位置 | 严重性 |
|---|------|------|--------|
| 1 | `cas_login_only_castgc` 不应使用子系统 service_url，直接用 CAS_LOGIN_URL 获取 CASTGC | `cas_login.py:206-207` | Bug |
| 2 | `class SessionPersistence(ABC)` 在 `redis_persistence.py` 中重复定义 | `redis_persistence.py:14` | 代码重复 |
| 3 | SubsystemSessionCache 作为 L1 + SessionPersistence 作为 L2 的两层缓存不必要，直接用 SessionPersistence 作为缓存即可 | `manager.py` | 架构冗余 |
| 4 | CASTGC 缓存在内存 dict 中，应迁移到 Redis | `manager.py:_castgc_cache` | 可靠性 |
| 5 | `password.py` 仅测试使用，生产代码未引用，可删除 | `password.py` | 死代码 |

## 设计

### 1. `cas_login_only_castgc` — 移除 service 参数

**文件**: `backend/app/core/session/cas_login.py:206-207`

CAS 服务器对 `/authserver/login` 的 POST 请求，如果不含 `service` 参数，会设置 `CASTGC` cookie 到 `.ca.csu.edu.cn` 域。这是正确的行为。

```python
# Before
service_url = SUBSYSTEM_SERVICE_URLS.get("jwc")
login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"

# After
login_url = CAS_LOGIN_URL  # "https://ca.csu.edu.cn/authserver/login"
```

**注意**: `cas_login` 函数（完整流程，获取子系统 session）保留 `service` 参数，因为需要通过 CAS 重定向到子系统来建立 session。

### 2. 移除 `redis_persistence.py` 中重复的 `SessionPersistence(ABC)`

**文件**: `backend/app/core/session/redis_persistence.py`

删除第 14 行的重复 ABC 定义。`persistence.py` 中已有权威定义：

```python
# redis_persistence.py — 移除以下内容
from abc import ABC, abstractmethod  # 移除 ABC

class SessionPersistence(ABC):  # 删除此重复定义
    @abstractmethod
    def save(...): pass
    @abstractmethod
    def load(...): pass
    @abstractmethod
    def invalidate(...): pass
```

### 3. 移除 SubsystemSessionCache，简化缓存为单层 Redis

**文件**: `backend/app/core/session/manager.py`

架构变更：移除 `SubsystemSessionCache` 实例，不再使用内存缓存层。

```
Before:
  get_session → _cache (内存 LRU, TTL 30min) → _persistence (Redis, TTL 30min) → provider

After:
  get_session → _persistence (Redis, TTL 30min) → provider
```

变更点：
- 删除 `from .cache import SubsystemSessionCache`
- 删除 `self._cache = SubsystemSessionCache(...)`
- `get_session()` 中移除所有 `_cache.get/set` 调用
- `invalidate_session()` 中移除 `_cache.invalidate()` 调用
- `_persistence` 仍是 RedisSessionPersistence 实例，作为唯一缓存层

### 4. CASTGC 缓存迁移至 Redis

**文件**: `backend/app/core/session/manager.py`

将 `self._castgc_cache: dict[str, dict]` 从内存 dict 迁移到 Redis。

**Key 格式**: `castgc:{user_id}`

**Value 格式**:
```json
{
  "castgc": "...",
  "created_at": 1712000000.0,
  "expires_at": 1712014400.0
}
```

**TTL**: 4 小时（`2 * 3600` → `4 * 3600`）

```python
# Key 方法
def _castgc_key(self, user_id: str) -> str:
    return f"castgc:{user_id}"

# _get_castgc — 从 Redis 读取
def _get_castgc(self, user_id: str) -> Optional[str]:
    data = self._redis.get(self._castgc_key(user_id))
    if not data:
        return None
    import json, time
    castgc_data = json.loads(data)
    if time.time() > castgc_data.get("expires_at", 0):
        self._redis.delete(self._castgc_key(user_id))
        return None
    return castgc_data.get("castgc")

# _save_castgc — 写入 Redis，TTL 4h
def _save_castgc(self, user_id: str, castgc: str) -> None:
    import json, time
    data = json.dumps({
        "castgc": castgc,
        "created_at": time.time(),
        "expires_at": time.time() + 4 * 3600,
    })
    self._redis.setex(self._castgc_key(user_id), 4 * 3600, data)
```

**注意**: `UnifiedSessionManager` 需要持有 Redis 连接（可复用 `RedisSessionPersistence` 的 `_redis` 实例）。

### 5. 删除 `password.py`

**文件**: `backend/app/core/session/password.py`

该文件仅测试使用，生产代码无引用。直接删除。

对应的测试文件 `backend/tests/core/session/test_password.py` 也一并删除。

## 文件变更汇总

| 操作 | 文件路径 |
|------|----------|
| 修改 | `backend/app/core/session/cas_login.py` |
| 修改 | `backend/app/core/session/redis_persistence.py` |
| 修改 | `backend/app/core/session/manager.py` |
| 修改 | `backend/app/core/session/persistence.py` |
| 删除 | `backend/app/core/session/password.py` |
| 删除 | `backend/tests/core/session/test_password.py` |

## 测试策略

1. **单元测试**: `cas_login_only_castgc` 的 `service` 参数行为
2. **集成测试**: 完整 login → get_session → invalidate 流程
3. **Redis 验证**: 确认 CASTGC key 存在且 TTL 正确
