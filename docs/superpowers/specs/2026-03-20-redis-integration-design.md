# Redis 集成设计

**日期**: 2026-03-20
**状态**: Approved
**类型**: 基础设施 + 功能重构

## 背景

项目需要引入 Redis 作为统一缓存层，支持：
1. Session 管理（替代 csu_sessions.json）
2. 对话历史缓存（减少 PostgreSQL IO）
3. CAS 登录时自动创建本地用户

## 架构设计

### Redis 部署架构

**采用方案 A**: 单一 Redis 实例 + Key 前缀隔离

```
Redis (localhost:6379, db=0)
├── session:{user_id}:{subsystem}  → CASTGC / 子系统 Session (TTL 2h)
└── history:{dialog_id}            → 对话历史列表 (LRU, TTL 1h)
```

### Key 命名规范

| 前缀 | 用途 | TTL |
|------|------|-----|
| `session:{user_id}:{subsystem}` | CAS 会话 (CASTGC + 子系统 Session) | 2 小时 |
| `history:{dialog_id}` | 对话历史缓存 | 1 小时 |

### LRU 策略

通过 Redis 配置实现：
```
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

## Task 1: Redis 基础设施

### 1.1 Docker 依赖

**文件**: `scripts/docker-compose-deps.yml`

添加 Redis 服务：
```yaml
redis:
  image: redis:7-alpine
  container_name: campusmind-redis
  ports:
    - "6379:6379"
  volumes:
    - campusmind_redis_data:/data
  command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
  healthcheck:
    test: ["CMD-SHELL", "redis-cli ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

### 1.2 环境变量

**文件**: `backend/.env` 和 `backend/.env.example`

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

### 1.3 Python 依赖

**文件**: `backend/pyproject.toml` (via uv)

```toml
[project]
dependencies = [
    "redis[hiredis]>=5.0.0",
]
```

---

## Task 2: Session 持久化 (Redis)

### 2.1 新增 RedisSessionPersistence

**文件**: `backend/app/core/session/redis_persistence.py`

```python
class RedisSessionPersistence(SessionPersistence):
    """Redis Session 持久化"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self._redis = redis.from_url(redis_url, decode_responses=True)

    def _key(self, user_id: str, subsystem: str) -> str:
        return f"session:{user_id}:{subsystem}"

    def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
        cookies_dict = {}
        for cookie in session.cookies:
            cookies_dict[cookie.name] = {
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "secure": cookie.secure,
            }
        data = json.dumps({"cookies": cookies_dict, "saved_at": time.time()})
        self._redis.setex(self._key(user_id, subsystem), ttl_seconds, data)

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        data = self._redis.get(self._key(user_id, subsystem))
        if not data:
            return None
        session = requests.Session()
        cookies_dict = json.loads(data).get("cookies", {})
        for name, info in cookies_dict.items():
            session.cookies.set(name, info["value"], domain=info.get("domain"))
        return session

    def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        if subsystem:
            self._redis.delete(self._key(user_id, subsystem))
        else:
            # 删除用户所有 session
            keys = self._redis.keys(f"session:{user_id}:*")
            if keys:
                self._redis.delete(*keys)
```

### 2.2 标记 FileSessionPersistence 为 deprecated

**文件**: `backend/app/core/session/persistence.py`

```python
class FileSessionPersistence(SessionPersistence):
    """
    [DEPRECATED] 文件存储 Session 持久化

    请使用 RedisSessionPersistence 替代。
    计划移除时间: 2026-06-01
    """
    ...
```

### 2.3 Factory 更新

**文件**: `backend/app/core/session/factory.py`

根据环境变量选择实现：
```python
def get_session_manager() -> UnifiedSessionManager:
    if settings.redis_url:
        persistence = RedisSessionPersistence(settings.redis_url)
    else:
        persistence = FileSessionPersistence()  # [DEPRECATED]
    ...
```

---

## Task 3: 对话历史 LRU 缓存

### 3.1 HistoryCacheService

**文件**: `backend/app/services/history/cache.py`

```python
import redis
import json
from typing import List, Optional
from app.config import settings
from app.services.history.history import HistoryService

class HistoryCacheService:
    """对话历史缓存服务 (Redis LRU)"""

    def __init__(self, redis_url: str = None):
        self._redis = redis.from_url(redis_url or settings.redis_url, decode_responses=True)
        self._history_service = HistoryService()
        self._ttl = 3600  # 1小时

    def _key(self, dialog_id: str) -> str:
        return f"history:{dialog_id}"

    async def get_history(self, dialog_id: str) -> Optional[List[dict]]:
        """获取对话历史，先查缓存，未命中查 DB"""
        # 1. 查 Redis
        cached = self._redis.get(self._key(dialog_id))
        if cached:
            return json.loads(cached)

        # 2. 查 DB
        histories = await self._history_service.get_history_by_dialog(dialog_id)
        if histories:
            # 放入缓存
            data = json.dumps([h.to_dict() for h in histories])
            self._redis.setex(self._key(dialog_id), self._ttl, data)

        return histories

    def invalidate(self, dialog_id: str) -> None:
        """使对话历史缓存失效"""
        self._redis.delete(self._key(dialog_id))
```

### 3.2 修改 completion.py 使用缓存

**文件**: `backend/app/api/v1/completion.py`

在 `generate_stream()` 中使用 `HistoryCacheService.get_history()` 替代直接查询 DB。

---

## Task 4: CAS 登录自动建户

### 4.1 Auth Service 修改

**文件**: `backend/app/api/v1/auth.py`

```python
from app.database.models import User

async def _ensure_user_exists(user_id: str) -> None:
    """如果用户不存在则创建"""
    session = async_session_dependency()
    existing = await session.get(User, user_id)
    if not existing:
        user = User(id=user_id, username=user_id)
        session.add(user)
        await session.commit()
```

在 `login()` 成功获取 CASTGC 后调用：
```python
# 登录成功后确保用户存在
await _ensure_user_exists(request.username)
```

---

## 耦合度分析

| | Task 1 | Task 2 | Task 3 | Task 4 |
|---|---|---|---|---|
| **Task 1** | — | **强依赖** | **强依赖** | 无依赖 |
| **Task 2** | 强依赖 | — | 无依赖 | 无依赖 |
| **Task 3** | 强依赖 | 无依赖 | — | 无依赖 |
| **Task 4** | 无依赖 | 无依赖 | 无依赖 | — |

**说明**:
- Task 1 是基础，Task 2/3 强依赖
- Task 2 (Session) 和 Task 3 (History) 无相互依赖
- Task 4 独立，可并行

---

## 实施顺序

1. **Task 1** — Redis 基础设施（Docker + 配置）
2. **Task 2** — Session Redis 持久化
3. **Task 3** — 历史缓存（可与 Task 2 并行）
4. **Task 4** — CAS 自动建户（可与 Task 2/3 并行）

---

## 测试策略

**Task 1**: `docker compose -f scripts/docker-compose-deps.yml up -d redis` → `redis-cli ping` 返回 PONG

**Task 2**: 登录后 `redis-cli KEYS "session:*"` 存在 key

**Task 3**: 对话后 `redis-cli KEYS "history:*"` 存在 key，再次请求命中缓存（Redis GET 不为空）

**Task 4**: 新用户登录后 `SELECT * FROM users WHERE id='new_user_id'`
