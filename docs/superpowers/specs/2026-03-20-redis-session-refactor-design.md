# Redis Session Refactor Design

**Date**: 2026-03-20
**Status**: Approved
**Type**: Architecture Refactor
**Supersedes**: `2026-03-20-three-tasks-design.md`

## Overview

Refactor Redis client initialization to use a global connection pool singleton managed via FastAPI lifespan, convert to async driver (`redis.asyncio`), and use FastAPI `Depends` for dependency injection in `HistoryCacheService`.

## Goals

1. **Redis History Sync**: Fix cache update on write (write-through strategy)
2. **FastAPI Depends**: Replace manual `HistoryCacheService()` instantiation with `Depends()`
3. **Global Singleton**: Single Redis connection pool managed via `app.state` + lifespan

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Lifespan                        │
│  startup: 创建全局 Redis 连接池 → 存入 app.state.redis        │
│  shutdown: 关闭连接池                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              app.state.redis (全局单例)                       │
│         redis.asyncio.Redis(connection_pool=...)            │
└─────────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
┌─────────────────────┐        ┌─────────────────────────────┐
│  HistoryCacheService │        │  RedisSessionPersistence     │
│  - get_history()     │        │  - save()                   │
│  - update_cache()    │        │  - load()                   │
│  - invalidate()      │        │  - invalidate()              │
└─────────────────────┘        └─────────────────────────────┘
```

## Components

### 1. Global Redis Client (`app/core/session/redis_client.py`)

**New file** providing global Redis connection pool singleton.

```python
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

def get_redis() -> Redis:
    """Get global Redis client (raises if not initialized)."""
    if _redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return _redis_client
```

### 2. FastAPI Dependency (`app/api/dependencies.py`)

Add `get_redis` as a FastAPI dependency.

```python
from app.core.session.redis_client import get_redis

async def get_redis_client() -> Redis:
    """FastAPI dependency for Redis client."""
    return get_redis()
```

### 3. HistoryCacheService (`app/services/history/cache.py`)

**Changes**:
- Accept `redis: Redis = Depends(get_redis_client)` instead of creating own connection
- Add `update_cache(dialog_id, histories)` method for write-through
- `get_history()` updates cache on write-through strategy

```python
class HistoryCacheService:
    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis
        self._ttl = 3600

    def _key(self, dialog_id: str) -> str:
        return f"history:{dialog_id}"

    async def get_history(self, dialog_id: str) -> Optional[List[dict]]:
        cached = await self._redis.get(self._key(dialog_id))
        if cached:
            return json.loads(cached)
        # ... fallback to DB, then update cache via update_cache()

    async def update_cache(self, dialog_id: str, histories: List[dict]) -> None:
        """Write-through: update cache after DB write."""
        data = json.dumps([h.to_dict() if hasattr(h, 'to_dict') else h for h in histories])
        await self._redis.setex(self._key(dialog_id), self._ttl, data)

    def invalidate(self, dialog_id: str) -> None:
        await self._redis.delete(self._key(dialog_id))
```

### 4. RedisSessionPersistence (`app/core/session/redis_persistence.py`)

**Changes**:
- Accept `redis: Redis = Depends(get_redis_client)` instead of own connection
- Convert sync methods to async

```python
class RedisSessionPersistence(SessionPersistence):
    def __init__(self, redis: Redis = Depends(get_redis_client)):
        self._redis = redis

    async def save(self, user_id: str, subsystem: str, session: requests.Session, ttl_seconds: int) -> None:
        # ... same logic but with await

    async def load(self, user_id: str, subsystem: str) -> Optional[requests.Session]:
        # ... same logic but with await

    async def invalidate(self, user_id: str, subsystem: Optional[str] = None) -> None:
        # ... same logic but with await
```

### 5. Config (`app/config.py`)

Add `redis_url` to `Settings`.

```python
class Settings(BaseModel):
    # ... existing fields
    redis_url: str = "redis://localhost:6379/0"

    @classmethod
    def from_env(cls):
        return cls(
            # ... existing fields
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        )
```

### 6. Lifespan (`app/main.py`)

Update lifespan to manage Redis lifecycle.

```python
from app.core.session.redis_client import init_redis, close_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing database tables...")
    create_db_and_tables()

    logger.info("Initializing Redis connection pool...")
    await init_redis(settings.redis_url)

    yield

    # Shutdown
    logger.info("Closing Redis connection pool...")
    await close_redis()
```

## Data Flow: Write-Through Cache

```
1. User message arrives → save to DB (ChatHistory)
2. After DB commit → call HistoryCacheService.update_cache(dialog_id, histories)
3. update_cache() writes new state to Redis with TTL
4. Next read → cache hit, return immediately
```

## Files Summary

| File | Action |
|------|--------|
| `app/core/session/redis_client.py` | **NEW** - Global Redis client singleton |
| `app/config.py` | **MODIFY** - Add `redis_url` field |
| `app/main.py` | **MODIFY** - Add Redis init/close in lifespan |
| `app/api/dependencies.py` | **MODIFY** - Add `get_redis_client` dependency |
| `app/services/history/cache.py` | **MODIFY** - Use Depends, add update_cache, make async |
| `app/core/session/redis_persistence.py` | **MODIFY** - Use Depends, convert to async |
| `app/api/v1/completion.py` | **MODIFY** - Use Depends for HistoryCacheService |

## Coupling Analysis

| | Task 1 | Task 2 | Task 3 |
|---|---|---|---|
| **Task 1** | — | **High** | **High** |
| **Task 2** | **High** | — | **High** |
| **Task 3** | **High** | **High** | — |

**Conclusion**: All three tasks are tightly coupled and must be implemented as a single unit.

## Testing Strategy

1. **Unit Tests**: Mock `get_redis_client`, test `HistoryCacheService` in isolation
2. **Integration Tests**: Test full flow with test Redis container
3. **E2E Tests**: Call `/completion/stream` and verify:
   - History is persisted to DB
   - Cache is updated (write-through)
   - Subsequent requests read from cache

## Migration Notes

- Existing Redis data is preserved (only key format may change)
- `RedisSessionPersistence` changes are backward compatible for session data
- `HistoryCacheService` cache may be cold after deploy (TTL will repopulate)
