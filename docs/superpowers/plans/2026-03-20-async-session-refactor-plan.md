# Async Session Manager - JwcService Refactor Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix async/sync mismatch where `get_jwc_session()`, `get_library_session()`, `get_ecard_session()`, `get_oa_session()` and `ToolContext.get_subsystem_session()` now return coroutines instead of sessions because they call async `get_session()`.

**Architecture:** Convert `JwcService` to async and update all callers to properly await. Also fix `ToolContext.get_subsystem_session()` to be async and update its callers.

**Tech Stack:** Python async/await, LangChain tools, FastAPI

---

## File Structure

```
backend/app/core/
├── context.py                 # FIX: ToolContext.get_subsystem_session() async
├── tools/jwc/
│   ├── service.py             # MODIFY: JwcService async
│   └── tools.py              # MODIFY: tool functions async
└── tools/oa/
    └── __init__.py           # MODIFY: OA tools async (uses get_subsystem_session)

backend/app/core/session/
├── manager.py                 # ALREADY DONE: async wrappers
└── factory.py                # No change needed
```

---

## Chunk 1: Fix ToolContext.get_subsystem_session()

**Files:**
- Modify: `backend/app/core/context.py`

### Task 1: Make get_subsystem_session async

- [ ] **Step 1: Read context.py**

Read `backend/app/core/context.py` to understand the current implementation.

- [ ] **Step 2: Make get_subsystem_session async**

Replace line 36-52 with:

```python
async def get_subsystem_session(self, subsystem: str) -> Optional[Dict[str, Any]]:
    """
    获取子系统 session，必要时自动登录

    注意：当前版本 UnifiedSessionManager.get_session 会自动处理登录
    """
    if not self.is_authenticated:
        logger.warning(f"User not authenticated, cannot get subsystem session for {subsystem}")
        return None

    try:
        # 从 session_manager 获取 session
        session = await self.session_manager.get_session(self.user_id, subsystem)
        return session
    except Exception as e:
        logger.error(f"Failed to get subsystem session for {subsystem}: {e}")
        return None
```

- [ ] **Step 3: Run test to verify syntax**

```bash
python3 -c "from app.core.context import ToolContext; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/context.py
git commit -m "refactor: make get_subsystem_session async"
```

---

## Chunk 2: Convert JwcService to Async

**Files:**
- Modify: `backend/app/core/tools/jwc/service.py`

### Task 2: Make JwcService async

- [ ] **Step 1: Read service.py**

Read `backend/app/core/tools/jwc/service.py` to understand the current implementation.

- [ ] **Step 2: Convert _get_client to async**

Change line 19-22 from:
```python
def _get_client(self, user_id: str) -> JwcClient:
    session = self._session_manager.get_jwc_session(user_id)
    return JwcClient(session)
```

To:
```python
async def _get_client(self, user_id: str) -> JwcClient:
    session = await self._session_manager.get_jwc_session(user_id)
    return JwcClient(session)
```

- [ ] **Step 3: Convert get_grades to async**

Change line 24-36 from:
```python
def get_grades(self, user_id: str, term: str = "") -> List[Grade]:
    client = self._get_client(user_id)
    return client.get_grades(term)
```

To:
```python
async def get_grades(self, user_id: str, term: str = "") -> List[Grade]:
    client = await self._get_client(user_id)
    return client.get_grades(term)
```

- [ ] **Step 4: Convert get_schedule, get_rank, get_level_exams similarly**

```python
async def get_schedule(self, user_id: str, term: str, week: str = "0") -> tuple[List[ClassEntry], str]:
    client = await self._get_client(user_id)
    return client.get_class_schedule(term, week)

async def get_rank(self, user_id: str) -> List[RankEntry]:
    client = await self._get_client(user_id)
    return client.get_rank()

async def get_level_exams(self, user_id: str) -> List[LevelExamEntry]:
    client = await self._get_client(user_id)
    return client.get_level_exams()
```

- [ ] **Step 5: Verify syntax**

```bash
python3 -c "from app.core.tools.jwc.service import JwcService; print('OK')"
```

- [ ] **Step 6: Commit**

```bash
git add backend/app/core/tools/jwc/service.py
git commit -m "refactor: make JwcService async"
```

---

## Chunk 3: Update Jwc Tools to Async

**Files:**
- Modify: `backend/app/core/tools/jwc/tools.py`

### Task 3: Update top-level tool functions (lines 83-173)

These are the standalone tool functions that create their own JwcService.

- [ ] **Step 1: Make _get_jwc_service_factory async**

Change from:
```python
def _get_jwc_service_factory() -> "JwcService":
    from app.core.session.manager import UnifiedSessionManager
    return JwcService(session_manager)
```

To:
```python
async def _get_jwc_service_factory() -> "JwcService":
    from app.core.session.manager import UnifiedSessionManager
    return JwcService(session_manager)
```

- [ ] **Step 2: Make _get_grades async**

Change from:
```python
def _get_grades(user_id: str, term: str = "") -> str:
    service = _get_jwc_service_factory()
    grades = service.get_grades(user_id, term)
    return _format_grades(grades)
```

To:
```python
async def _get_grades(user_id: str, term: str = "") -> str:
    service = await _get_jwc_service_factory()
    grades = await service.get_grades(user_id, term)
    return _format_grades(grades)
```

- [ ] **Step 3: Similarly update _get_schedule, _get_rank, _get_level_exams**

```python
async def _get_schedule(user_id: str, term: str, week: str = "0") -> str:
    service = await _get_jwc_service_factory()
    classes, start_week_day = await service.get_schedule(user_id, term, week)
    result = _format_schedule(classes)
    if start_week_day:
        result += f"\n\n> 学期第1周开始于: {start_week_day}日"
    return result

async def _get_rank(user_id: str) -> str:
    service = await _get_jwc_service_factory()
    ranks = await service.get_rank(user_id)
    return _format_ranks(ranks)

async def _get_level_exams(user_id: str) -> str:
    service = await _get_jwc_service_factory()
    exams = await service.get_level_exams(user_id)
    return _format_level_exams(exams)
```

- [ ] **Step 4: Verify syntax**

```bash
python3 -c "from app.core.tools.jwc.tools import _get_grades, _get_schedule; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/tools/jwc/tools.py
git commit -m "refactor: make jwc tool functions async"
```

---

## Chunk 4: Update create_jwc_tools() Inner Functions

**Files:**
- Modify: `backend/app/core/tools/jwc/tools.py` (lines 234-331)

### Task 4: Update inner tool functions in create_jwc_tools()

- [ ] **Step 1: Update _get_jwc_service_factory inside create_jwc_tools**

Change from:
```python
def _get_jwc_service_factory() -> "JwcService":
    from app.core.session.manager import UnifiedSessionManager
    return JwcService(session_manager)
```

To:
```python
async def _get_jwc_service_factory() -> "JwcService":
    from app.core.session.manager import UnifiedSessionManager
    return JwcService(session_manager)
```

- [ ] **Step 2: Update _get_grades inside create_jwc_tools**

Change from:
```python
def _get_grades(term: str = "") -> str:
    if not ctx.is_authenticated:
        return "请先登录后再查询成绩"

    session = ctx.get_subsystem_session("jwc")
    if not session:
        return "教务系统会话已过期，请重新登录"

    try:
        service = _get_jwc_service_factory()
        grades = service.get_grades(ctx.user_id, term)
        return _format_grades(grades)
    except Exception as e:
        logger.error(f"成绩查询失败: {e}")
        return f"成绩查询失败: {str(e)}"
```

To:
```python
async def _get_grades(term: str = "") -> str:
    if not ctx.is_authenticated:
        return "请先登录后再查询成绩"

    session = await ctx.get_subsystem_session("jwc")
    if not session:
        return "教务系统会话已过期，请重新登录"

    try:
        service = await _get_jwc_service_factory()
        grades = await service.get_grades(ctx.user_id, term)
        return _format_grades(grades)
    except Exception as e:
        logger.error(f"成绩查询失败: {e}")
        return f"成绩查询失败: {str(e)}"
```

- [ ] **Step 3: Similarly update _get_schedule, _get_rank, _get_level_exams inside create_jwc_tools**

```python
async def _get_schedule(term: str, week: str = "0") -> str:
    if not ctx.is_authenticated:
        return "请先登录后再查询课表"

    session = await ctx.get_subsystem_session("jwc")
    if not session:
        return "教务系统会话已过期，请重新登录"

    try:
        service = await _get_jwc_service_factory()
        classes, start_week_day = await service.get_schedule(ctx.user_id, term, week)
        result = _format_schedule(classes)
        if start_week_day:
            result += f"\n\n> 学期第1周开始于: {start_week_day}日"
        return result
    except Exception as e:
        logger.error(f"课表查询失败: {e}")
        return f"课表查询失败: {str(e)}"

async def _get_rank() -> str:
    if not ctx.is_authenticated:
        return "请先登录后再查询排名"

    session = await ctx.get_subsystem_session("jwc")
    if not session:
        return "教务系统会话已过期，请重新登录"

    try:
        service = await _get_jwc_service_factory()
        ranks = await service.get_rank(ctx.user_id)
        return _format_ranks(ranks)
    except Exception as e:
        logger.error(f"排名查询失败: {e}")
        return f"排名查询失败: {str(e)}"

async def _get_level_exams() -> str:
    if not ctx.is_authenticated:
        return "请先登录后再查询等级考试成绩"

    session = await ctx.get_subsystem_session("jwc")
    if not session:
        return "教务系统会话已过期，请重新登录"

    try:
        service = await _get_jwc_service_factory()
        exams = await service.get_level_exams(ctx.user_id)
        return _format_level_exams(exams)
    except Exception as e:
        logger.error(f"等级考试查询失败: {e}")
        return f"等级考试查询失败: {str(e)}"
```

- [ ] **Step 4: Verify syntax**

```bash
python3 -c "from app.core.tools.jwc.tools import create_jwc_tools; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/tools/jwc/tools.py
git commit -m "refactor: make create_jwc_tools inner functions async"
```

---

## Chunk 5: Update OA Tools

**Files:**
- Modify: `backend/app/core/tools/oa/__init__.py`

### Task 5: Update OA tools that use get_subsystem_session

- [ ] **Step 1: Read the file and find usages of get_subsystem_session**

```bash
grep -n "get_subsystem_session" backend/app/core/tools/oa/__init__.py
```

- [ ] **Step 2: Update all get_subsystem_session calls to await**

Change from:
```python
session = ctx.get_subsystem_session("oa")
```

To:
```python
session = await ctx.get_subsystem_session("oa")
```

- [ ] **Step 3: Verify syntax**

```bash
python3 -c "from app.core.tools.oa import *; print('OK')"
```

- [ ] **Step 4: Commit**

```bash
git add backend/app/core/tools/oa/__init__.py
git commit -m "refactor: make oa tools async"
```

---

## Chunk 6: Verification

### Task 6: Run all tests

- [ ] **Step 1: Run pytest**

```bash
cd backend && .venv/bin/python -m pytest tests/core/tools/jwc/ -v --tb=short
```

- [ ] **Step 2: If tests fail, fix and retry**

- [ ] **Step 3: Commit final verification**

```bash
git add -A && git commit -m "test: verify async refactor works"
```

---

## Summary

| Chunk | Task | Files | Status |
|-------|------|-------|--------|
| 1 | Fix ToolContext | context.py | |
| 2 | JwcService async | service.py | |
| 3 | JwcTools async (top-level) | tools.py | |
| 4 | create_jwc_tools async | tools.py | |
| 5 | OA tools async | oa/__init__.py | |
| 6 | Verification | - | |

**Total files modified:** 5
