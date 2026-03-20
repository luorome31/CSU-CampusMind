# CAS Session Bug Fixes — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 5 bugs in the CAS session management code: correct `cas_login_only_castgc` service URL, remove duplicate ABC, simplify cache architecture, move CASTGC to Redis, delete dead password.py.

**Architecture:** Single-tier Redis caching for session persistence. CASTGC stored in Redis with 4h TTL. SubsystemSessionCache removed entirely. Memory dict replaced by Redis for all caching.

**Tech Stack:** Python, requests, redis, pytest

---

## File Overview

| File | Role |
|------|------|
| `backend/app/core/session/cas_login.py` | CAS login logic; fix line 206-207 |
| `backend/app/core/session/redis_persistence.py` | Redis session persistence; remove duplicate ABC |
| `backend/app/core/session/persistence.py` | Abstract base class; remove FileSessionPersistence |
| `backend/app/core/session/manager.py` | Unified session manager; remove cache, add CASTGC Redis |
| `backend/app/core/session/cache.py` | SubsystemSessionCache; will become unused after Task 3 |
| `backend/app/core/session/password.py` | Dead code; delete |
| `backend/tests/core/session/test_password.py` | Test for dead code; delete |

---

## Task Coupling

```
Task 1 (cas_login fix) ──── independent ────► Task 5 (password.py delete)
Task 2 (remove duplicate ABC) ──► Task 3 (remove cache) ──► Task 4 (CASTGC Redis)
```

Execute in order: **1 → 2 → 3 → 4 → 5** (Tasks 1 and 5 are independently testable but modifying the same files, so sequential is cleaner)

---

## Chunk 1: Fix cas_login_only_castgc service URL

### Task 1: Fix cas_login_only_castgc — remove service parameter

**Files:**
- Modify: `backend/app/core/session/cas_login.py:182-257`
- Test: `backend/tests/core/session/test_cas_login.py` (existing)

- [ ] **Step 1: Verify existing test for cas_login_only_castgc**

Run: `grep -n "cas_login_only_castgc\|service_url\|service=" backend/tests/core/session/test_cas_login.py`

Expected: Shows how `cas_login_only_castgc` is currently tested regarding service URL

- [ ] **Step 2: Edit cas_login.py lines 205-207**

```python
# Before (lines 205-207):
        # 任选一个 service_url，只需要能获取 CASTGC
        service_url = SUBSYSTEM_SERVICE_URLS.get("jwc")
        login_url = f"{CAS_LOGIN_URL}?service={requests.utils.quote(service_url)}"

# After (lines 205-206):
        # 直接使用 CAS_LOGIN_URL，不需要 service 参数即可获取 CASTGC
        login_url = CAS_LOGIN_URL
```

- [ ] **Step 3: Verify no other uses of SUBSYSTEM_SERVICE_URLS in cas_login.py**

Run: `grep -n "SUBSYSTEM_SERVICE_URLS" backend/app/core/session/cas_login.py`

Expected: No results (the constant should not be used in this file after the fix)

- [ ] **Step 4: Run existing tests**

Run: `cd backend && python -m pytest tests/core/session/test_cas_login.py -v -k "castgc" 2>&1 | head -40`

Expected: Tests pass (or fail with a clear reason if CAS server unavailable)

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session/cas_login.py
git commit -m "fix(session): remove service param from cas_login_only_castgc

CASTGC is obtained by POSTing to CAS_LOGIN_URL without service param.
The service parameter is only needed for the full cas_login flow that
also establishes subsystem session."
```

---

## Chunk 2: Remove duplicate SessionPersistence ABC

### Task 2: Remove duplicate SessionPersistence ABC from redis_persistence.py

**Files:**
- Modify: `backend/app/core/session/redis_persistence.py`
- Test: `backend/tests/core/session/test_redis_persistence.py` (existing)

- [ ] **Step 1: Review current redis_persistence.py structure**

Run: `head -30 backend/app/core/session/redis_persistence.py`

Expected: Lines 1-13 are imports, line 14 starts with `class SessionPersistence(ABC):`

- [ ] **Step 2: Edit redis_persistence.py — remove duplicate ABC definition**

Change from:
```python
# Lines 1-13: imports including:
from abc import ABC, abstractmethod

# Lines 14-27: duplicate ABC definition to DELETE:
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


class RedisSessionPersistence(SessionPersistence):  # This line becomes line 14
```

To:
```python
# Lines 1-12: imports, remove 'abstractmethod' from import
from abc import ABC  # remove abstractmethod — no longer needed here

# Lines 13+: class RedisSessionPersistence(SessionPersistence):  ← line 13 now
```

- [ ] **Step 3: Verify RedisSessionPersistence still inherits from SessionPersistence**

Run: `grep -n "class RedisSessionPersistence" backend/app/core/session/redis_persistence.py`

Expected: `class RedisSessionPersistence(SessionPersistence):` — inheritance is from persistence.py, not the removed local ABC

- [ ] **Step 4: Run redis persistence tests**

Run: `cd backend && python -m pytest tests/core/session/test_redis_persistence.py -v 2>&1 | head -40`

Expected: All pass (or fail with unrelated reason)

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session/redis_persistence.py
git commit -m "fix(session): remove duplicate SessionPersistence ABC from redis_persistence

persistence.py is the canonical location for the ABC.
redis_persistence.py only needs to define RedisSessionPersistence."
```

---

## Chunk 3: Simplify manager.py — remove SubsystemSessionCache

### Task 3: Remove SubsystemSessionCache from UnifiedSessionManager

**Files:**
- Modify: `backend/app/core/session/manager.py`
- Modify: `backend/app/core/session/cache.py` (optional, leave for reference)
- Test: `backend/tests/core/session/test_manager.py` (existing or create)

- [ ] **Step 1: Review current manager.py get_session flow**

Run: `sed -n '119,163p' backend/app/core/session/manager.py`

Expected: Shows `_cache.get/set` calls in get_session method

- [ ] **Step 2: Edit manager.py — remove SubsystemSessionCache**

Changes to `__init__`:
```python
# REMOVE from imports:
from .cache import SubsystemSessionCache

# REMOVE from __init__:
self._cache = SubsystemSessionCache(ttl_seconds=ttl_seconds)

# KEEP: self._persistence = persistence
# KEEP: self._rate_limiter = rate_limiter or LoginRateLimiter()
# KEEP: self._ttl = ttl_seconds
```

Changes to `get_session`:
```python
# REMOVE: cached = self._cache.get(user_id, subsystem)
# REMOVE: if cached: return cached.session  (the entire L1 check)

# REMOVE: self._cache.set(user_id, subsystem, loaded_session) after persistence load
# REMOVE: self._cache.set(user_id, subsystem, session) after provider fetch

# KEEP: persistence.load → provider.fetch → persistence.save → return
```

Changes to `invalidate_session`:
```python
# REMOVE: self._cache.invalidate(user_id, subsystem)
# KEEP: self._persistence.invalidate(user_id, subsystem)
```

- [ ] **Step 3: Verify no remaining _cache references**

Run: `grep -n "_cache\|SubsystemSessionCache" backend/app/core/session/manager.py`

Expected: No results

- [ ] **Step 4: Run manager tests**

Run: `cd backend && python -m pytest tests/core/session/test_manager.py -v 2>&1 | head -50`

Expected: Tests pass (may need updates if they test cache behavior)

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session/manager.py
git commit -m "refactor(session): remove SubsystemSessionCache, use persistence only

Session persistence (Redis) is the single cache layer.
get_session flow: persistence.load → provider.fetch → persistence.save"
```

---

## Chunk 4: Move CASTGC from in-memory dict to Redis

### Task 4: Replace _castgc_cache dict with Redis storage

**Files:**
- Modify: `backend/app/core/session/manager.py`
- Test: `backend/tests/core/session/test_manager.py`

- [ ] **Step 1: Review current CASTGC methods**

Run: `sed -n '71,101p' backend/app/core/session/manager.py`

Expected: Shows `_castgc_cache: dict[str, dict]`, `_get_castgc`, `_save_castgc`

- [ ] **Step 2: Edit manager.py — add Redis CASTGC methods**

Add a helper method:
```python
def _castgc_key(self, user_id: str) -> str:
    return f"castgc:{user_id}"
```

Replace `_get_castgc`:
```python
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
```

Replace `_save_castgc`:
```python
def _save_castgc(self, user_id: str, castgc: str) -> None:
    import json, time
    data = json.dumps({
        "castgc": castgc,
        "created_at": time.time(),
        "expires_at": time.time() + 4 * 3600,  # 4 hours TTL
    })
    self._redis.setex(self._castgc_key(user_id), 4 * 3600, data)
```

Also update `invalidate_session` to clear CASTGC from Redis:
```python
# In invalidate_session, replace CASTGC dict deletion:
# REMOVE: del self._castgc_cache[user_id]
# ADD: self._redis.delete(self._castgc_key(user_id))
```

- [ ] **Step 3: Verify UnifiedSessionManager holds Redis connection**

Run: `grep -n "self._redis\|self._persistence" backend/app/core/session/manager.py`

Expected: `self._persistence` is passed in and is a `RedisSessionPersistence`. Access `self._persistence._redis` for the Redis client.

- [ ] **Step 4: Run tests**

Run: `cd backend && python -m pytest tests/core/session/test_manager.py -v 2>&1 | head -50`

Expected: Tests pass

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/session/manager.py
git commit -m "feat(session): store CASTGC in Redis with 4h TTL

Replace in-memory _castgc_cache dict with Redis storage.
Key format: castgc:{user_id}, TTL: 4 hours."
```

---

## Chunk 5: Delete password.py dead code

### Task 5: Delete password.py and its test

**Files:**
- Delete: `backend/app/core/session/password.py`
- Delete: `backend/tests/core/session/test_password.py`

- [ ] **Step 1: Verify no production imports of password.py**

Run: `grep -rn "from.*password\|import.*password\|PasswordManager" backend/app/`

Expected: No results (only test files should match)

- [ ] **Step 2: Delete files**

```bash
rm backend/app/core/session/password.py
rm backend/tests/core/session/test_password.py
```

- [ ] **Step 3: Verify imports are clean**

Run: `grep -rn "from.*password\|import.*password\|PasswordManager" backend/app/ backend/tests/`

Expected: No results

- [ ] **Step 4: Commit**

```bash
git add -A  # stages both deletions
git commit -m "chore(session): delete unused PasswordManager

password.py was only referenced by tests, not production code.
Removing dead code reduces maintenance surface."
```

---

## Final Integration

After all 5 tasks complete, run the full test suite:

```bash
cd backend && python -m pytest tests/core/session/ -v 2>&1
```

Expected: All session tests pass.

Then merge the worktree back to dev:

```bash
git checkout dev
git merge 2026-03-20-cas-session-refactor-fixes --no-ff -m "fix(session): 5 targeted bug fixes per 2026-03-20 spec"
git worktree remove .claude/worktrees/2026-03-20-cas-session-refactor-fixes
git branch -d 2026-03-20-cas-session-refactor-fixes
```
