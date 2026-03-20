# Redis Session Refactor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor Redis client initialization to use a global connection pool singleton managed via FastAPI lifespan, convert to async driver (`redis.asyncio`), and use FastAPI `Depends` for dependency injection.

**Architecture:** Global Redis connection pool via `app.state` + lifespan, shared by `HistoryCacheService` and `RedisSessionPersistence`. Write-through cache strategy for history sync.

**Tech Stack:** `redis.asyncio`, FastAPI `Depends`, SQLModel, `sqlalchemy.ext.asyncio`

---

## File Structure

```
backend/app/
├── core/session/
│   ├── redis_client.py          # NEW: Global Redis client singleton
│   ├── redis_persistence.py     # MODIFY: Use global client, convert to async
│   ├── manager.py               # MODIFY: Update to async persistence methods
│   └── factory.py               # MODIFY: Update to use async RedisSessionPersistence
├── api/
│   ├── dependencies.py          # MODIFY: Add get_redis_client dependency
│   └── v1/completion.py         # MODIFY: Use Depends for HistoryCacheService
├── services/history/
│   └── cache.py                 # MODIFY: Use Depends, add update_cache, async
├── config.py                    # MODIFY: Add redis_url field
└── main.py                      # MODIFY: Add Redis lifecycle in lifespan
```

## Important: UnifiedSessionManager Coupling

`UnifiedSessionManager` accesses `self._persistence._redis` directly for CASTGC operations (lines 83, 90, 93, 104, 181). Since we cannot change the interface of `RedisSessionPersistence` without breaking `UnifiedSessionManager`, we will keep `RedisSessionPersistence` with a `_redis` attribute (now pointing to the global client). The CASTGC methods will still work, but `save/load/invalidate` will become async.

---

## Chunk 1: Global Redis Client Singleton

**Files:**
- Create: `backend/app/core/session/redis_client.py`
- Modify: `backend/app/config.py`

### Task 1: Add `redis_url` to Settings

**Files:**
- Modify: `backend/app/config.py:43-87`

- [ ] **Step 1: Add redis_url field to Settings class**

Modify `backend/app/config.py` - add `redis_url` field after `session_ttl_seconds`:

```python
# JWC Session Storage
session_storage_path: str = "./data/csu_sessions.json"
session_ttl_seconds: int = 30 * 60  # 30 minutes

# Redis
redis_url: str = "redis://localhost:6379/0"  # NEW
```

- [ ] **Step 2: Add redis_url to from_env()**

Modify `backend/app/config.py` - add `redis_url` to the `from_env()` method:

```python
session_storage_path=os.getenv("SESSION_STORAGE_PATH", "./data/csu_sessions.json"),
session_ttl_seconds=int(os.getenv("SESSION_TTL_SECONDS", "1800")),
redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),  # NEW
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/config.py
git commit -m "feat(config): add redis_url setting"
```

### Task 2: Create Global Redis Client Module

**Files:**
- Create: `backend/app/core/session/redis_client.py`

- [ ] **Step 1: Write redis_client.py**

Create `backend/app/core/session/redis_client.py`:

```python
"""
Global Redis Client Singleton

Manages Redis connection pool lifecycle via FastAPI lifespan.
Uses redis.asyncio for full async support.
"""
from typing import Optional
from redis.asyncio import Redis, ConnectionPool

_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[Redis] = None


async def init_redis(redis_url: str) -> Redis:
    """Initialize global Redis connection pool on startup."""
    global _redis_pool, _redis_client
    _redis_pool = ConnectionPool.from_url(redis_url, decode_responses=True)
    _redis_client = Redis(connection_pool=_redis_pool)
    return _redis_client


async def close_redis():
    """Close Redis connection pool on shutdown."""
    global _redis_pool, _redis_client
    if _redis_client:
        await _redis_client.aclose()
    if _redis_pool:
        await _redis_pool.disconnect()
    _redis_client = None
    _redis_pool = None


def get_redis() -> Redis:
    """Get global Redis client (raises if not initialized)."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client


def is_redis_initialized() -> bool:
    """Check if Redis client is initialized."""
    return _redis_client is not None
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/session/redis_client.py
git commit -m "feat(session): add global Redis client singleton"
```

---

## Chunk 2: Update main.py Lifespan

**Files:**
- Modify: `backend/app/main.py`

### Task 3: Add Redis Lifecycle to Lifespan

**Files:**
- Modify: `backend/app/main.py:1-82`

- [ ] **Step 1: Update imports in main.py**

Add Redis imports to `backend/app/main.py`:

```python
from app.core.session.redis_client import init_redis, close_redis
```

- [ ] **Step 2: Update lifespan function**

Replace the existing `lifespan` function (lines 27-38):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup and shutdown logic."""
    logger.info("Initializing database tables...")
    try:
        create_db_and_tables()
        logger.info(f"Database initialized: {settings.database_url}")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

    logger.info("Initializing Redis connection pool...")
    try:
        await init_redis(settings.redis_url)
        logger.info(f"Redis initialized: {settings.redis_url}")
    except Exception as e:
        logger.error(f"Redis initialization failed: {e}")
        # Redis is optional for some features, don't fail startup

    yield

    logger.info("Shutting down...")
    await close_redis()
```

- [ ] **Step 3: Commit**

```bash
git add backend/app/main.py
git commit -m "feat(main): add Redis lifecycle management to lifespan"
```

---

## Chunk 3: Add FastAPI Dependency for Redis

**Files:**
- Modify: `backend/app/api/dependencies.py`

### Task 4: Add get_redis_client Dependency

**Files:**
- Modify: `backend/app/api/dependencies.py`

- [ ] **Step 1: Add get_redis_client dependency**

Add to `backend/app/api/dependencies.py`:

```python
from redis.asyncio import Redis
from app.core.session.redis_client import get_redis


async def get_redis_client() -> Redis:
    """FastAPI dependency for Redis client."""
    return get_redis()
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/api/dependencies.py
git commit -m "feat(dependencies): add get_redis_client FastAPI dependency"
```

---

## Chunk 4: Refactor HistoryCacheService

**Files:**
- Modify: `backend/app/services/history/cache.py`

### Task 5: Refactor HistoryCacheService to Use Depends + Async

**Files:**
- Modify: `backend/app/services/history/cache.py`

- [ ] **Step 1: Write updated cache.py**

Replace `backend/app/services/history/cache.py` with:

```python
"""
对话历史缓存服务

使用 Redis LRU 缓存对话历史，减少数据库 IO。
Write-through 策略：写入时同时更新缓存。
"""
import json
from typing import List, Optional

from redis.asyncio import Redis

from app.config import settings
from app.api.dependencies import get_redis_client


class HistoryCacheService:
    """
    对话历史缓存服务 (Redis LRU)

    先查缓存，未命中查 DB，然后写入缓存。
    写入时使用 write-through 策略：保存 DB 后同时更新缓存。
    """

    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis
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
        cached = await self._redis.get(self._key(dialog_id))
        if cached:
            return json.loads(cached)

        # 2. 查 DB (延迟导入避免循环)
        from app.services.history.history import HistoryService
        from app.database.session import async_session_dependency

        async for session in async_session_dependency():
            history_service = HistoryService()
            histories = await history_service.get_history_by_dialog(session, dialog_id)

            if not histories:
                return None

            # 3. 写入缓存 (write-through)
            await self.update_cache(dialog_id, histories)

            return histories

    async def update_cache(self, dialog_id: str, histories: List) -> None:
        """
        Write-through: 更新缓存

        Args:
            dialog_id: 对话 ID
            histories: ChatHistory 对象列表
        """
        data = json.dumps([h.to_dict() for h in histories])
        await self._redis.setex(self._key(dialog_id), self._ttl, data)

    async def invalidate(self, dialog_id: str) -> None:
        """使对话历史缓存失效"""
        await self._redis.delete(self._key(dialog_id))
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/services/history/cache.py
git commit -m "refactor(cache): use Depends for Redis, add write-through update_cache"
```

---

## Chunk 5: Refactor RedisSessionPersistence

**Files:**
- Modify: `backend/app/core/session/redis_persistence.py`

### Task 6: Refactor RedisSessionPersistence to Use Global Client + Async

**Files:**
- Modify: `backend/app/core/session/redis_persistence.py`

**Important:** The `UnifiedSessionManager` accesses `self._persistence._redis` directly for CASTGC operations. We must maintain `_redis` as a property that returns the global client.

- [ ] **Step 1: Write updated redis_persistence.py**

Replace `backend/app/core/session/redis_persistence.py` with:

```python
"""
Redis Session 持久化实现

使用 Redis 替代 FileSessionPersistence 提供会话存储。
使用全局 Redis 连接池单例。
"""
import json
import time
from typing import Optional
import requests
from redis.asyncio import Redis

from app.api.dependencies import get_redis_client
from .persistence import SessionPersistence


class RedisSessionPersistence(SessionPersistence):
    """
    Redis Session 持久化

    Key 格式: session:{user_id}:{subsystem}
    """

    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis

    def _key(self, user_id: str, subsystem: str) -> str:
        return f"session:{user_id}:{subsystem}"

    async def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
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
        await self._redis.setex(self._key(user_id, subsystem), ttl_seconds, data)

    async def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        data = await self._redis.get(self._key(user_id, subsystem))
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

    async def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        if subsystem:
            await self._redis.delete(self._key(user_id, subsystem))
        else:
            # 删除用户所有 session
            keys = []
            async for key in self._redis.scan_iter(f"session:{user_id}:*"):
                keys.append(key)
            if keys:
                await self._redis.delete(*keys)
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/session/redis_persistence.py
git commit -m "refactor(persistence): use global Redis client, convert to async"
```

---

## Chunk 6: Update UnifiedSessionManager for Async Persistence

**Files:**
- Modify: `backend/app/core/session/manager.py`

### Task 7: Update UnifiedSessionManager to Use Async Persistence

**Files:**
- Modify: `backend/app/core/session/manager.py`

**Note:** `UnifiedSessionManager._get_castgc`, `_save_castgc`, and `invalidate_session` access `self._persistence._redis` directly for CASTGC operations. Since `_redis` is now the global Redis client (still sync-compatible), these will continue to work. However, `get_session` calls `load` and `save` which are now async.

- [ ] **Step 1: Update manager.py imports**

Add `hasattr` check for async persistence:

```python
# No new imports needed, just update methods below
```

- [ ] **Step 2: Update get_session method**

Replace `get_session` method (lines 123-158) with async version:

```python
async def get_session(self, user_id: str, subsystem: str) -> requests.Session:
    """
    获取指定子系统的会话

    流程：
    1. 检查持久化缓存 → 存在且有效? → 直接返回
    2. 获取 CASTGC
    3. 若无 CASTGC，抛出 NeedReLoginError
    4. 使用 SubsystemSessionProvider 获取子系统 session
    5. 持久化保存 session

    Raises:
        NeedReLoginError: CASTGC 不存在或过期，需要重新登录
    """
    # 1. 检查持久化缓存
    loaded_session = await self._persistence.load(user_id, subsystem)
    if loaded_session:
        logger.info(f"Loaded session from persistence for {user_id}:{subsystem}")
        return loaded_session

    # 2. 获取 CASTGC
    castgc = self._get_castgc(user_id)
    if not castgc:
        raise NeedReLoginError(
            f"用户 {user_id} 的 CASTGC 已过期或不存在，请重新登录"
        )

    # 3. 使用 Provider 获取子系统 session
    provider = SubsystemSessionProvider.get_provider(subsystem)
    session = provider.fetch_session(castgc)

    # 4. 持久化保存
    await self._persistence.save(user_id, subsystem, session, self._ttl)

    logger.info(f"Fetched new session for {user_id}:{subsystem}")
    return session
```

- [ ] **Step 3: Update invalidate_session method**

Replace `invalidate_session` method (lines 176-181) with async version:

```python
async def invalidate_session(self, user_id: str, subsystem: Optional[str] = None) -> None:
    """使会话失效"""
    await self._persistence.invalidate(user_id, subsystem)
    # 如果指定 subsystem 为 None，清除所有子系统的 session，同时也清除 CASTGC
    if subsystem is None:
        await self._persistence._redis.delete(self._castgc_key(user_id))
```

- [ ] **Step 4: Update helper methods to be async**

Replace `_get_castgc` and `_save_castgc` methods (lines 76-104) - these still use sync Redis access via `_redis` but need to be called properly:

```python
def _get_castgc(self, user_id: str) -> Optional[str]:
    """
    获取缓存的 CASTGC cookie

    Returns:
        CASTGC 值，如果不存在或过期返回 None
    """
    import asyncio
    # Run sync Redis operation in thread pool since _redis is sync
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(self._persistence._redis.get(self._castgc_key(user_id)))
    if not data:
        return None
    try:
        castgc_data = json.loads(data)
    except json.JSONDecodeError:
        logger.warning(f"Corrupted CASTGC data for user {user_id}, discarding")
        loop.run_until_complete(self._persistence._redis.delete(self._castgc_key(user_id)))
        return None
    if time.time() > castgc_data.get("expires_at", 0):
        loop.run_until_complete(self._persistence._redis.delete(self._castgc_key(user_id)))
        return None
    return castgc_data.get("castgc")

def _save_castgc(self, user_id: str, castgc: str) -> None:
    """保存 CASTGC cookie，TTL 4小时"""
    import asyncio
    data = json.dumps({
        "castgc": castgc,
        "created_at": time.time(),
        "expires_at": time.time() + 4 * 3600,  # 4 hours TTL
    })
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        self._persistence._redis.setex(self._castgc_key(user_id), 4 * 3600, data)
    )
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session/manager.py
git commit -m "refactor(manager): update UnifiedSessionManager for async persistence"
```

---

## Chunk 7: Update Session Factory

**Files:**
- Modify: `backend/app/core/session/factory.py`

### Task 8: Update Session Factory

**Files:**
- Modify: `backend/app/core/session/factory.py`

- [ ] **Step 1: Update factory to not pass redis_url**

Modify `backend/app/core/session/factory.py` - `RedisSessionPersistence` no longer needs `redis_url` since it uses global client:

```python
def create_session_manager() -> UnifiedSessionManager:
    """创建 SessionManager 实例"""
    # 根据配置选择持久化实现
    if settings.redis_url:
        persistence = RedisSessionPersistence()  # No redis_url needed, uses global client
    else:
        persistence = FileSessionPersistence(
            storage_path=settings.session_storage_path
        )  # [DEPRECATED]

    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=settings.session_ttl_seconds,
    )

    logger.info("SessionManager 实例已创建")
    return manager
```

- [ ] **Step 2: Commit**

```bash
git add backend/app/core/session/factory.py
git commit -m "refactor(factory): update RedisSessionPersistence instantiation"
```

---

## Chunk 8: Update completion.py to Use Depends

**Files:**
- Modify: `backend/app/api/v1/completion.py`

### Task 9: Update completion.py to Use Depends for HistoryCacheService

**Files:**
- Modify: `backend/app/api/v1/completion.py`

- [ ] **Step 1: Update imports**

Update imports in `backend/app/api/v1/completion.py` (around line 33):

```python
# Change:
from app.services.history.cache import HistoryCacheService

# To:
from app.services.history.cache import HistoryCacheService, get_history_cache_service
```

- [ ] **Step 2: Update generate_stream function signature**

Modify `generate_stream` function (around line 158) to accept cache_service as parameter instead of instantiating:

```python
async def generate_stream(
    agent: ReactAgent,
    message: str,
    knowledge_ids: List[str],
    session: AsyncSession,
    dialog_id: str,
    model: str,
    cache_service: HistoryCacheService,  # NEW: injected via Depends
) -> AsyncGenerator[str, None]:
```

- [ ] **Step 3: Update cache_service usage**

Replace the manual instantiation (line 189):
```python
cache_service = HistoryCacheService()
histories = await cache_service.get_history(dialog_id)
```

With the injected service (this is already done via parameter).

- [ ] **Step 4: Update callers to pass cache_service**

Update `completion_stream` endpoint (line 257) to use Depends:

```python
from app.services.history.cache import HistoryCacheService, get_history_cache_service

async def completion_stream(
    request: CompletionRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency),
    cache_service: HistoryCacheService = Depends(get_history_cache_service),  # NEW
):
```

Then pass `cache_service` to `generate_stream`:
```python
return WatchedStreamingResponse(
    content=generate_stream(
        agent=agent,
        message=request.message,
        knowledge_ids=request.knowledge_ids,
        session=db,
        dialog_id=dialog.id,
        model=request.model,
        cache_service=cache_service,  # NEW
    ),
    ...
)
```

- [ ] **Step 5: Add get_history_cache_service dependency**

Add to `backend/app/api/v1/completion.py`:

```python
async def get_history_cache_service(
    redis: Redis = Depends(get_redis_client),
) -> HistoryCacheService:
    """FastAPI dependency for HistoryCacheService."""
    return HistoryCacheService(redis=redis)
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/v1/completion.py
git commit -m "refactor(completion): use Depends for HistoryCacheService"
```

---

## Chunk 9: Integration Testing

### Task 10: Write Integration Tests

**Files:**
- Create: `backend/tests/core/session/test_redis_client.py`
- Create: `backend/tests/services/history/test_cache.py`

- [ ] **Step 1: Write redis_client unit test**

Create `backend/tests/core/session/test_redis_client.py`:

```python
"""
Tests for global Redis client singleton
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from redis.asyncio import Redis

from app.core.session import redis_client


class TestRedisClient:
    """Tests for redis_client module"""

    def test_get_redis_raises_when_not_initialized(self):
        """Test that get_redis() raises RuntimeError before init"""
        # Reset module state
        redis_client._redis_client = None
        redis_client._redis_pool = None

        with pytest.raises(RuntimeError, match="Redis not initialized"):
            redis_client.get_redis()

    def test_is_redis_initialized_false_before_init(self):
        """Test is_redis_initialized returns False before init"""
        redis_client._redis_client = None
        redis_client._redis_pool = None

        assert redis_client.is_redis_initialized() is False

    def test_is_redis_initialized_true_after_init(self):
        """Test is_redis_initialized returns True after init"""
        mock_redis = MagicMock(spec=Redis)
        redis_client._redis_client = mock_redis
        redis_client._redis_pool = MagicMock()

        assert redis_client.is_redis_initialized() is True

        # Cleanup
        redis_client._redis_client = None
        redis_client._redis_pool = None

    @pytest.mark.asyncio
    async def test_init_and_close_redis(self):
        """Test init_redis and close_redis flow"""
        mock_pool = AsyncMock()
        mock_client = AsyncMock(spec=Redis)

        with patch.object(redis_client.ConnectionPool, 'from_url', return_value=mock_pool):
            with patch.object(redis_client.Redis, '__init__', return_value=None):
                with patch.object(redis_client.Redis, 'connection_pool', mock_pool):
                    mock_client.connection_pool = mock_pool
                    redis_client._redis_client = None
                    redis_client._redis_pool = None

                    result = await redis_client.init_redis("redis://localhost:6379/0")

                    assert redis_client._redis_client is not None
                    assert redis_client._redis_pool is not None

                    # Cleanup
                    await redis_client.close_redis()
```

- [ ] **Step 2: Write cache service test**

Create `backend/tests/services/history/test_cache.py`:

```python
"""
Tests for HistoryCacheService
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from dataclasses import dataclass

from app.services.history.cache import HistoryCacheService


@dataclass
class MockChatHistory:
    """Mock ChatHistory with to_dict method"""
    id: str
    dialog_id: str
    role: str
    content: str
    created_at: str = "2024-01-01T00:00:00"

    def to_dict(self):
        return {
            "id": self.id,
            "dialog_id": self.dialog_id,
            "role": self.role,
            "content": self.content,
            "created_at": self.created_at,
        }


class TestHistoryCacheService:
    """Tests for HistoryCacheService"""

    @pytest.fixture
    def mock_redis(self):
        """Create a mock async Redis client"""
        return AsyncMock()

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create HistoryCacheService with mock Redis"""
        return HistoryCacheService(redis=mock_redis)

    def test_key_format(self, cache_service):
        """Test cache key format"""
        assert cache_service._key("dialog123") == "history:dialog123"

    @pytest.mark.asyncio
    async def test_get_history_cache_hit(self, cache_service, mock_redis):
        """Test get_history returns cached data"""
        cached_data = '[{"id": "1", "role": "user", "content": "hello"}]'
        mock_redis.get = AsyncMock(return_value=cached_data)

        result = await cache_service.get_history("dialog123")

        assert result is not None
        assert len(result) == 1
        assert result[0]["content"] == "hello"
        mock_redis.get.assert_called_once_with("history:dialog123")

    @pytest.mark.asyncio
    async def test_update_cache(self, cache_service, mock_redis):
        """Test update_cache writes to Redis"""
        mock_redis.setex = AsyncMock()
        histories = [
            MockChatHistory(id="1", dialog_id="d1", role="user", content="hi")
        ]

        await cache_service.update_cache("dialog123", histories)

        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args
        assert call_args[0][0] == "history:dialog123"
        assert call_args[0][1] == 3600  # TTL

    @pytest.mark.asyncio
    async def test_invalidate(self, cache_service, mock_redis):
        """Test invalidate deletes cache key"""
        mock_redis.delete = AsyncMock()

        await cache_service.invalidate("dialog123")

        mock_redis.delete.assert_called_once_with("history:dialog123")
```

- [ ] **Step 3: Run tests**

```bash
cd backend && python -m pytest tests/core/session/test_redis_client.py tests/services/history/test_cache.py -v
```

- [ ] **Step 4: Commit**

```bash
git add backend/tests/core/session/test_redis_client.py backend/tests/services/history/test_cache.py
git commit -m "test: add Redis client and cache service tests"
```

---

## Chunk 10: Final Integration Verification

### Task 11: End-to-End Verification

- [ ] **Step 1: Start Redis locally (if not running)**

```bash
redis-server --daemonize yes
```

- [ ] **Step 2: Run the application**

```bash
cd backend && python -m uvicorn app.main:app --reload
```

- [ ] **Step 3: Check logs for successful startup**

Expected logs:
```
INFO - Initializing database tables...
INFO - Database initialized: <url>
INFO - Initializing Redis connection pool...
INFO - Redis initialized: redis://localhost:6379/0
```

- [ ] **Step 4: Test completion endpoint**

```bash
curl -X POST http://localhost:8000/api/v1/completion/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "hello", "dialog_id": "test-dialog-123"}'
```

- [ ] **Step 5: Verify Redis has cache key**

```bash
redis-cli GET "history:test-dialog-123"
```

---

## Summary

| Chunk | Task | Files | Status |
|-------|------|-------|--------|
| 1 | Global Redis Client | config.py, redis_client.py | |
| 2 | Lifespan | main.py | |
| 3 | Dependencies | dependencies.py | |
| 4 | HistoryCacheService | cache.py | |
| 5 | RedisSessionPersistence | redis_persistence.py | |
| 6 | UnifiedSessionManager | manager.py | |
| 7 | Session Factory | factory.py | |
| 8 | completion.py | completion.py | |
| 9 | Tests | test_redis_client.py, test_cache.py | |
| 10 | E2E Verification | - | |

**Total files modified:** 9
**Total files created:** 3 (redis_client.py, test_redis_client.py, test_cache.py)
