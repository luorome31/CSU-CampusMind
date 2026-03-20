# Redis 集成实现计划

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 引入 Redis 基础设施，实现 Session 管理（替代 csu_sessions.json）、对话历史 LRU 缓存、用户自动创建

**Architecture:**
- 单一 Redis 实例 + Key 前缀隔离
- `session:{user_id}:{subsystem}` 用于会话管理
- `history:{dialog_id}` 用于对话历史缓存 (LRU)
- 新增 `RedisSessionPersistence`，标记 `FileSessionPersistence` 为 deprecated

**Tech Stack:** Docker, Redis 7 Alpine, redis-py, FastAPI, SQLModel

---

## Chunk 1: Redis 基础设施

### Task 1.1: 添加 Redis Docker 服务

**Files:**
- Modify: `scripts/docker-compose-deps.yml`

- [ ] **Step 1: 添加 Redis 服务到 docker-compose-deps.yml**

在 `elasticsearch` 服务后添加：

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

同时在 `volumes` 部分添加：
```yaml
volumes:
  campusmind_postgres_data:
  campusmind_minio_data:
  campusmind_elasticsearch_data:
  campusmind_elasticsearch_plugins:
  campusmind_redis_data:  # 新增
```

- [ ] **Step 2: 测试 Redis 服务启动**

Run: `cd /home/luorome/software/CampusMind && docker compose -f scripts/docker-compose-deps.yml up -d redis`
Run: `docker compose -f scripts/docker-compose-deps.yml ps` (确认 redis 状态为 healthy)
Run: `docker exec campusmind-redis redis-cli ping` (应返回 PONG)

- [ ] **Step 3: 提交**

```bash
git add scripts/docker-compose-deps.yml
git commit -m "feat(deps): add Redis 7 service to docker-compose-deps"
```

---

### Task 1.2: 添加 Redis 环境变量

**Files:**
- Modify: `backend/.env`
- Modify: `backend/.env.example`

- [ ] **Step 1: 在 backend/.env 添加 Redis 配置**

在文件末尾添加：
```bash
# ===========================================
# Redis Configuration
# ===========================================
REDIS_URL=redis://localhost:6379/0
```

- [ ] **Step 2: 在 backend/.env.example 添加 Redis 配置**

在 Database Configuration 注释后添加：
```bash
# ===========================================
# Redis Configuration
# ===========================================
REDIS_URL=redis://localhost:6379/0
```

- [ ] **Step 3: 提交**

```bash
git add backend/.env backend/.env.example
git commit -m "feat(config): add REDIS_URL environment variable"
```

---

### Task 1.3: 添加 Redis Python 依赖

**Files:**
- Modify: `backend/pyproject.toml`

- [ ] **Step 1: 检查当前 pyproject.toml 依赖格式**

Run: `cd /home/luorome/software/CampusMind/backend && head -50 pyproject.toml`

- [ ] **Step 2: 添加 redis 依赖**

在 dependencies 数组中添加 `"redis[hiredis]>=5.0.0",`

- [ ] **Step 3: 更新 uv .lock**

Run: `cd /home/luorome/software/CampusMind/backend && uv sync`

- [ ] **Step 4: 验证安装**

Run: `uv run python -c "import redis; print(redis.__version__)"`

- [ ] **Step 5: 提交**

```bash
git add pyproject.toml uv.lock
git commit -m "feat(deps): add redis[hiredis]>=5.0.0 dependency"
```

---

## Chunk 2: Session 持久化 (Redis)

### Task 2.1: 实现 RedisSessionPersistence

**Files:**
- Create: `backend/app/core/session/redis_persistence.py`
- Test: `backend/tests/core/session/test_redis_persistence.py`

- [ ] **Step 1: 编写测试**

```python
# backend/tests/core/session/test_redis_persistence.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.core.session.redis_persistence import RedisSessionPersistence


class TestRedisSessionPersistence:
    """测试 RedisSessionPersistence"""

    @pytest.fixture
    def mock_redis(self):
        with patch("app.core.session.redis_persistence.redis") as mock:
            yield mock

    def test_key_format(self, mock_redis):
        """验证 key 格式"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        key = impl._key("user123", "jwc")
        assert key == "session:user123:jwc"

    def test_save_serializes_cookies(self, mock_redis):
        """save 应正确序列化 cookies"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis

        mock_session = MagicMock()
        mock_session.cookies = [
            MagicMock(name="CASTGC", value="abc123", domain="ca.csu.edu.cn", path="/", secure=True),
        ]

        impl.save("user123", "jwc", mock_session, 1800)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "session:user123:jwc"
        assert call_args[0][1] == 1800

    def test_load_returns_session(self, mock_redis):
        """load 应返回重建的 session"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis

        import json
        mock_redis.get.return_value = json.dumps({
            "cookies": {"CASTGC": {"value": "abc123", "domain": "ca.csu.edu.cn"}},
            "saved_at": 1234567890.0
        })

        result = impl.load("user123", "jwc")

        assert result is not None
        result.cookies.set.assert_called_once_with("CASTGC", "abc123", domain="ca.csu.edu.cn")

    def test_load_returns_none_when_missing(self, mock_redis):
        """key 不存在时返回 None"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        mock_redis.get.return_value = None

        result = impl.load("user123", "jwc")

        assert result is None

    def test_invalidate_deletes_key(self, mock_redis):
        """invalidate 应删除指定 key"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis

        impl.invalidate("user123", "jwc")

        mock_redis.delete.assert_called_once_with("session:user123:jwc")

    def test_invalidate_all_deletes_user_keys(self, mock_redis):
        """subsystem=None 时删除用户所有 session keys"""
        impl = RedisSessionPersistence.__new__(RedisSessionPersistence)
        impl._redis = mock_redis
        mock_redis.keys.return_value = ["session:user123:jwc", "session:user123:library"]

        impl.invalidate("user123")

        mock_redis.keys.assert_called_once_with("session:user123:*")
        mock_redis.delete.assert_called_once()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_redis_persistence.py -v`
Expected: ERROR (file not found)

- [ ] **Step 3: 实现 RedisSessionPersistence**

```python
# backend/app/core/session/redis_persistence.py
"""
Redis Session 持久化实现

使用 Redis 替代 FileSessionPersistence 提供会话存储。
"""
import json
import time
import threading
from abc import ABC, abstractmethod
from typing import Optional
import requests
import redis


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


class RedisSessionPersistence(SessionPersistence):
    """
    Redis Session 持久化

    Key 格式: session:{user_id}:{subsystem}
    """

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

        data = json.dumps({
            "cookies": cookies_dict,
            "saved_at": time.time()
        })
        self._redis.setex(self._key(user_id, subsystem), ttl_seconds, data)

    def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        data = self._redis.get(self._key(user_id, subsystem))
        if not data:
            return None

        session = requests.Session()
        cookies_dict = json.loads(data).get("cookies", {})

        for name, info in cookies_dict.items():
            session.cookies.set(
                name,
                info["value"],
                domain=info.get("domain"),
                path=info.get("path", "/"),
                secure=info.get("secure", False),
            )

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

- [ ] **Step 4: 运行测试验证通过**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/core/session/test_redis_persistence.py -v`
Expected: PASS (6 tests)

- [ ] **Step 5: 提交**

```bash
git add backend/app/core/session/redis_persistence.py backend/tests/core/session/test_redis_persistence.py
git commit -m "feat(session): add RedisSessionPersistence implementation"
```

---

### Task 2.2: 标记 FileSessionPersistence 为 deprecated

**Files:**
- Modify: `backend/app/core/session/persistence.py`

- [ ] **Step 1: 添加 deprecation 注释**

在 `FileSessionPersistence` 类上添加：
```python
class FileSessionPersistence(SessionPersistence):
    """
    [DEPRECATED] 文件存储 Session 持久化

    请使用 RedisSessionPersistence 替代。
    计划移除时间: 2026-06-01
    """
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/core/session/persistence.py
git commit -m "deprecate(session): mark FileSessionPersistence as deprecated"
```

---

### Task 2.3: 更新 Factory 使用 Redis

**Files:**
- Modify: `backend/app/core/session/factory.py`

- [ ] **Step 1: 读取当前 factory.py**

Run: `cat /home/luorome/software/CampusMind/backend/app/core/session/factory.py`

- [ ] **Step 2: 修改 factory.py 使用 RedisSessionPersistence**

```python
from app.config import settings
from .redis_persistence import RedisSessionPersistence
from .persistence import FileSessionPersistence

def get_session_manager() -> UnifiedSessionManager:
    # 根据配置选择持久化实现
    if settings.redis_url:
        persistence = RedisSessionPersistence(settings.redis_url)
    else:
        persistence = FileSessionPersistence()  # [DEPRECATED]

    return UnifiedSessionManager(persistence=persistence)
```

- [ ] **Step 3: 验证语法**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.core.session.factory import get_session_manager; print('Factory OK')"`

- [ ] **Step 4: 提交**

```bash
git add backend/app/core/session/factory.py
git commit -m "feat(session): use RedisSessionPersistence when REDIS_URL is configured"
```

---

## Chunk 3: 对话历史 LRU 缓存

### Task 3.1: 实现 HistoryCacheService

**Files:**
- Create: `backend/app/services/history/cache.py`
- Test: `backend/tests/services/history/test_cache.py`

- [ ] **Step 1: 编写测试**

```python
# backend/tests/services/history/test_cache.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.history.cache import HistoryCacheService


class TestHistoryCacheService:
    """测试 HistoryCacheService"""

    @pytest.fixture
    def mock_redis(self):
        with patch("app.services.history.cache.redis") as mock:
            yield mock

    @pytest.fixture
    def mock_history_service(self):
        with patch("app.services.history.cache.HistoryService") as mock:
            yield mock

    def test_key_format(self, mock_redis):
        """验证 key 格式"""
        impl = HistoryCacheService.__new__(HistoryCacheService)
        impl._redis = mock_redis
        key = impl._key("dialog123")
        assert key == "history:dialog123"

    def test_invalidate_calls_delete(self, mock_redis):
        """invalidate 应删除 key"""
        impl = HistoryCacheService.__new__(HistoryCacheService)
        impl._redis = mock_redis

        impl.invalidate("dialog123")

        mock_redis.delete.assert_called_once_with("history:dialog123")
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/services/history/test_cache.py -v`
Expected: ERROR (file not found)

- [ ] **Step 3: 实现 HistoryCacheService**

```python
# backend/app/services/history/cache.py
"""
对话历史缓存服务

使用 Redis LRU 缓存对话历史，减少数据库 IO。
"""
import json
from typing import List, Optional
import redis

from app.config import settings


class HistoryCacheService:
    """
    对话历史缓存服务 (Redis LRU)

    先查缓存，未命中查 DB，然后写入缓存。
    """

    def __init__(self, redis_url: str = None):
        self._redis = redis.from_url(redis_url or settings.redis_url, decode_responses=True)
        self._ttl = 3600  # 1小时

    def _key(self, dialog_id: str) -> str:
        return f"history:{dialog_id}"

    async def get_history(self, dialog_id: str) -> Optional[List[dict]]:
        """
        获取对话历史

        流程:
        1. 查 Redis 缓存
        2. 未命中则查 DB
        3. 写入缓存
        """
        # 1. 查 Redis
        cached = self._redis.get(self._key(dialog_id))
        if cached:
            return json.loads(cached)

        # 2. 查 DB (延迟导入避免循环)
        from app.services.history.history import HistoryService
        history_service = HistoryService()
        histories = await history_service.get_history_by_dialog(dialog_id)

        if not histories:
            return None

        # 3. 写入缓存
        data = json.dumps([h.to_dict() for h in histories])
        self._redis.setex(self._key(dialog_id), self._ttl, data)

        return histories

    def invalidate(self, dialog_id: str) -> None:
        """使对话历史缓存失效"""
        self._redis.delete(self._key(dialog_id))
```

- [ ] **Step 4: 运行测试验证通过**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/services/history/test_cache.py -v`
Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add backend/app/services/history/cache.py backend/tests/services/history/test_cache.py
git commit -m "feat(history): add HistoryCacheService with Redis LRU caching"
```

---

### Task 3.2: 修改 completion.py 使用缓存

**Files:**
- Modify: `backend/app/api/v1/completion.py`

- [ ] **Step 1: 读取 completion.py 找到 generate_stream 函数**

Run: `grep -n "async def generate_stream\|def generate_stream" /home/luorome/software/CampusMind/backend/app/api/v1/completion.py`

- [ ] **Step 2: 在文件开头添加 HistoryCacheService 导入**

```python
from app.services.history.cache import HistoryCacheService
```

- [ ] **Step 3: 在 generate_stream 函数中替换 HistoryService 调用**

找到:
```python
histories = await HistoryService.get_history_by_dialog(session, dialog_id)
```

替换为:
```python
cache_service = HistoryCacheService()
histories = await cache_service.get_history(dialog_id)
```

- [ ] **Step 4: 验证语法**

Run: `cd /home/luorome/software/CampusMind/backend && uv run python -c "from app.api.v1.completion import router; print('Completion router OK')"`

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/v1/completion.py
git commit -m "feat(completion): use HistoryCacheService for dialog history"
```

---

## Chunk 4: CAS 登录自动建户

### Task 4.1: 实现用户自动创建

**Files:**
- Modify: `backend/app/api/v1/auth.py`
- Test: `backend/tests/api/v1/test_auth_auto_create.py`

- [ ] **Step 1: 编写测试**

```python
# backend/tests/api/v1/test_auth_auto_create.py
import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestAuthAutoCreateUser:
    """测试 CAS 登录时自动创建用户"""

    @pytest.mark.asyncio
    async def test_ensure_user_exists_creates_new_user(self):
        """新用户登录时应创建用户记录"""
        with patch("app.api.v1.auth.async_session_dependency") as mock_session_dep:
            mock_session = AsyncMock()
            mock_session.get = AsyncMock(return_value=None)  # 用户不存在
            mock_session.commit = AsyncMock()
            mock_session_dep.return_value = mock_session

            from app.api.v1.auth import _ensure_user_exists
            await _ensure_user_exists("student123")

            # 验证用户被添加和提交
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_user_exists_skips_existing(self):
        """已存在用户不应重复创建"""
        with patch("app.api.v1.auth.async_session_dependency") as mock_session_dep:
            mock_session = AsyncMock()
            existing_user = MagicMock()
            mock_session.get = AsyncMock(return_value=existing_user)  # 用户已存在
            mock_session_dep.return_value = mock_session

            from app.api.v1.auth import _ensure_user_exists
            await _ensure_user_exists("student123")

            # 验证用户未被添加
            mock_session.add.assert_not_called()
```

- [ ] **Step 2: 运行测试验证失败**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/api/v1/test_auth_auto_create.py -v`
Expected: ERROR (function not found)

- [ ] **Step 3: 实现 _ensure_user_exists 函数**

在 `backend/app/api/v1/auth.py` 中添加：

```python
async def _ensure_user_exists(user_id: str) -> None:
    """
    如果用户不存在则创建

    Args:
        user_id: 用户 ID (CAS username)
    """
    from app.database.models import User

    session = async_session_dependency()
    existing = await session.get(User, user_id)
    if not existing:
        user = User(id=user_id, username=user_id)
        session.add(user)
        await session.commit()
```

- [ ] **Step 4: 在 login 函数中调用**

找到 login 函数中登录成功后的位置：
```python
# 4. 生成 JWT
token = jwt_manager.create_token({"user_id": request.username})
```

在之前添加：
```python
# 登录成功后确保用户存在
await _ensure_user_exists(request.username)

# 4. 生成 JWT
token = jwt_manager.create_token({"user_id": request.username})
```

- [ ] **Step 5: 运行测试验证**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/api/v1/test_auth_auto_create.py -v`
Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add backend/app/api/v1/auth.py backend/tests/api/v1/test_auth_auto_create.py
git commit -m "feat(auth): auto-create user on CAS login"
```

---

## Chunk 5: 集成测试

### Task 5.1: 端到端测试

**Files:**
- Test: `backend/tests/integration/test_redis_integration.py`

- [ ] **Step 1: 编写集成测试**

```python
# backend/tests/integration/test_redis_integration.py
"""
Redis 集成测试

测试完整的 Redis 使用场景:
1. Session 存储和读取
2. 历史缓存
3. CAS 登录自动建户
"""
import pytest
import redis


class TestRedisSessionIntegration:
    """Session Redis 集成测试"""

    def test_redis_connection(self):
        """验证 Redis 连接"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        r.set("test_key", "test_value")
        assert r.get("test_key") == "test_value"
        r.delete("test_key")

    def test_session_key_format(self):
        """验证 session key 格式"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        key = f"session:user123:jwc"
        r.setex(key, 60, "test_session")
        assert r.exists(key) == 1
        r.delete(key)


class TestRedisHistoryIntegration:
    """历史缓存 Redis 集成测试"""

    def test_history_key_format(self):
        """验证 history key 格式"""
        r = redis.from_url("redis://localhost:6379/0", decode_responses=True)
        key = "history:dialog123"
        r.setex(key, 60, '["msg1", "msg2"]')
        assert r.get(key) == '["msg1", "msg2"]'
        r.delete(key)
```

- [ ] **Step 2: 运行集成测试**

Run: `cd /home/luorome/software/CampusMind/backend && uv run pytest tests/integration/test_redis_integration.py -v`
Expected: PASS (假设 Redis 运行在 localhost:6379)

- [ ] **Step 3: 提交**

```bash
git add backend/tests/integration/test_redis_integration.py
git commit -m "test(integration): add Redis integration tests"
```

---

## 实施顺序

1. **Chunk 1**: Redis 基础设施 (Task 1.1, 1.2, 1.3)
2. **Chunk 2**: Session 持久化 (Task 2.1, 2.2, 2.3) — 强依赖 Chunk 1
3. **Chunk 3**: 历史缓存 (Task 3.1, 3.2) — 可与 Chunk 2 并行
4. **Chunk 4**: 自动建户 (Task 4.1) — 可与 Chunk 2/3 并行
5. **Chunk 5**: 集成测试

---

## 验证清单

- [ ] `docker compose -f scripts/docker-compose-deps.yml up -d redis` 成功
- [ ] `redis-cli ping` 返回 PONG
- [ ] `redis-cli KEYS "session:*"` 登录后存在 key
- [ ] `redis-cli KEYS "history:*"` 对话后存在 key
- [ ] 新用户登录后 users 表有记录
