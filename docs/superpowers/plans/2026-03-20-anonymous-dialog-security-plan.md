# Anonymous Dialog Security Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix IDOR vulnerability by centralizing dialog authorization; support anonymous dialogs via nullable user_id.

**Architecture:** New `DialogRepository` layer handles all dialog access with built-in authorization. `user_id` becomes nullable in both schema and model. Frontend provides `dialog_id` (UUID/thread_id) from browser storage.

**Tech Stack:** FastAPI, SQLModel, SQLAlchemy async, pytest (async)

---

## File Map

| File | Action |
|------|--------|
| `docs/database/schema.sql` | Modify: user_id nullable, FK SET NULL |
| `docs/database/database-design.md` | Modify: update dialogs table section |
| `app/database/models/dialog.py` | Modify: user_id Optional |
| `app/repositories/__init__.py` | Create: export DialogRepository |
| `app/repositories/dialog_repository.py` | Create: authorization-aware dialog access |
| `app/api/v1/completion.py` | Modify: use repo, remove client user_id |
| `app/services/dialog/dialog.py` | Modify: support Optional[user_id] |
| `tests/services/test_dialog_repository.py` | Create: repo tests (anonymous, auth, IDOR) |
| `tests/api/test_completion.py` | Modify: update for no user_id in request |

---

## Chunk 1: Schema & Model

### Task 1: Update schema.sql

**Files:**
- Modify: `docs/database/schema.sql:27-33`

- [ ] **Step 1: Update dialogs table definition**

Change lines 27-33 from:
```sql
CREATE TABLE IF NOT EXISTS dialogs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    agent_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

To:
```sql
CREATE TABLE IF NOT EXISTS dialogs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    agent_id TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

- [ ] **Step 2: Update tool_call_logs FK too (same SET NULL pattern)**

In lines 114-125, change:
```sql
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
```
(Should already be SET NULL — verify it.)

- [ ] **Step 3: Commit**

```bash
git add docs/database/schema.sql
git commit -m "fix(db): make dialogs.user_id nullable, use FK SET NULL"
```

---

### Task 2: Update Python Dialog model

**Files:**
- Modify: `app/database/models/dialog.py:22`

- [ ] **Step 1: Add Optional import and change user_id type**

In `dialog.py`, change:
```python
from typing import Optional
```
(Ensure it's imported)

Change line 22 from:
```python
user_id: str = Field(index=True, description="User ID")
```
To:
```python
user_id: Optional[str] = Field(default=None, index=True, description="User ID (NULL for anonymous)")
```

- [ ] **Step 2: Commit**

```bash
git add app/database/models/dialog.py
git commit -m "feat(model): make Dialog.user_id nullable for anonymous support"
```

---

## Chunk 2: Repository Layer

### Task 3: Create DialogRepository

**Files:**
- Create: `app/repositories/__init__.py`
- Create: `app/repositories/dialog_repository.py`

- [ ] **Step 1: Create repositories directory init**

```python
"""Repository layer for database access with authorization."""
from app.repositories.dialog_repository import DialogRepository

__all__ = ["DialogRepository"]
```

- [ ] **Step 2: Create DialogRepository with authorization logic**

```python
"""
Dialog Repository - Centralized dialog access with authorization.

Handles:
- Anonymous dialog creation (user_id=NULL)
- Authenticated dialog access (user_id must match JWT)
- IDOR prevention (cannot access another user's dialog)
"""
import uuid
from datetime import datetime
from typing import Optional, Tuple
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.dialog import Dialog


class DialogRepositoryError(Exception):
    """Base exception for dialog repository errors."""
    pass


class ForbiddenError(DialogRepositoryError):
    """Raised when user attempts to access a dialog they don't own."""
    pass


class DialogRepository:
    """Repository for dialog operations with built-in authorization."""

    @staticmethod
    async def get_or_create_dialog(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str],
        agent_id: Optional[str] = None,
    ) -> Tuple[Dialog, bool]:
        """
        Get existing dialog with authorization check, or create new.

        Authorization rules:
        - Anonymous (jwt_user_id=None): can only access dialogs with user_id=NULL
        - Logged-in: can only access dialogs where user_id matches jwt_user_id

        Args:
            session: Database session
            dialog_id: Dialog ID (UUID, provided by frontend as thread_id)
            jwt_user_id: User ID from JWT token (None if anonymous)
            agent_id: Optional agent ID for new dialogs

        Returns:
            Tuple of (dialog, created_new)

        Raises:
            ForbiddenError: user attempts to access another user's dialog
        """
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        existing = result.scalar_one_or_none()

        if existing is not None:
            # Dialog exists — check authorization
            if not DialogRepository._authorize_access(existing, jwt_user_id):
                raise ForbiddenError("Access denied to this dialog")
            # Update timestamp and return existing
            existing.updated_at = datetime.now()
            await session.commit()
            return existing, False

        # Dialog doesn't exist — create new
        # For anonymous users, user_id must be NULL
        # For logged-in users, user_id must match JWT
        new_dialog = Dialog(
            id=dialog_id,
            user_id=jwt_user_id,  # None for anonymous, actual ID for logged-in
            agent_id=agent_id,
            updated_at=datetime.now()
        )
        session.add(new_dialog)
        await session.commit()
        await session.refresh(new_dialog)
        return new_dialog, True

    @staticmethod
    def _authorize_access(dialog: Dialog, jwt_user_id: Optional[str]) -> bool:
        """
        Check if user is authorized to access a dialog.

        Rules:
        - Anonymous (jwt_user_id=None): can only access dialogs where user_id IS NULL
        - Logged-in: can only access dialogs where user_id matches jwt_user_id
        """
        if jwt_user_id is None:
            # Anonymous: only allow access to NULL user_id dialogs
            return dialog.user_id is None
        else:
            # Logged-in: must match user_id
            return dialog.user_id == jwt_user_id

    @staticmethod
    async def get_dialog_if_authorized(
        session: AsyncSession,
        dialog_id: str,
        jwt_user_id: Optional[str],
    ) -> Optional[Dialog]:
        """
        Get dialog only if user is authorized.

        Returns None if dialog doesn't exist or user is not authorized.
        Does NOT raise ForbiddenError — returns None silently.
        """
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        dialog = result.scalar_one_or_none()

        if dialog is None:
            return None

        if not DialogRepository._authorize_access(dialog, jwt_user_id):
            return None

        return dialog

    @staticmethod
    async def list_user_dialogs(
        session: AsyncSession,
        user_id: str,
        limit: int = 50
    ) -> list[Dialog]:
        """
        List all dialogs for a logged-in user.

        Args:
            session: Database session
            user_id: User ID (from JWT)
            limit: Maximum number of dialogs to return

        Returns:
            List of Dialog objects ordered by updated_at DESC
        """
        statement = (
            select(Dialog)
            .where(Dialog.user_id == user_id)
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())

    @staticmethod
    async def list_anonymous_dialogs(
        session: AsyncSession,
        limit: int = 50
    ) -> list[Dialog]:
        """
        List all anonymous dialogs (user_id IS NULL).

        Args:
            session: Database session
            limit: Maximum number of dialogs to return

        Returns:
            List of anonymous Dialog objects ordered by updated_at DESC
        """
        statement = (
            select(Dialog)
            .where(Dialog.user_id.is_(None))
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
        )
        result = await session.execute(statement)
        return list(result.scalars().all())
```

- [ ] **Step 3: Commit**

```bash
git add app/repositories/__init__.py app/repositories/dialog_repository.py
git commit -m "feat(repo): add DialogRepository with authorization"
```

---

### Task 4: Write DialogRepository tests

**Files:**
- Create: `tests/services/test_dialog_repository.py`

- [ ] **Step 1: Write tests for DialogRepository**

```python
"""
DialogRepository Tests - Authorization and anonymous dialog support
"""
import pytest
import os
import tempfile
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

from app.repositories.dialog_repository import (
    DialogRepository,
    ForbiddenError,
)
from app.database.models.dialog import Dialog
from app.database.models.chat_history import ChatHistory


@pytest.fixture(scope="function")
async def test_engine():
    """Create async test engine with SQLite"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db_url = f"sqlite+aiosqlite:///{path}"
    engine = create_async_engine(db_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield engine
    await engine.dispose()
    os.unlink(path)


@pytest.fixture(scope="function")
async def test_session(test_engine):
    """Create async session"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


class TestDialogRepositoryAnonymous:
    """Tests for anonymous dialog support"""

    @pytest.mark.asyncio
    async def test_create_anonymous_dialog(self, test_session):
        """Anonymous user can create a new dialog"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None,
            agent_id="test_agent"
        )
        assert created is True
        assert dialog.user_id is None
        assert dialog.id == "anon-thread-001"
        await test_session.commit()

    @pytest.mark.asyncio
    async def test_anonymous_can_access_own_dialog(self, test_session):
        """Anonymous user can continue their own dialog"""
        # Create first
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None
        )
        await test_session.commit()

        # Access again
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="anon-thread-001",
            jwt_user_id=None
        )
        assert created is False
        assert dialog.user_id is None
        assert dialog.id == "anon-thread-001"

    @pytest.mark.asyncio
    async def test_anonymous_cannot_access_logged_in_dialog(self, test_session):
        """Anonymous cannot access a dialog owned by a logged-in user"""
        # Create dialog owned by user_1
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        await test_session.commit()

        # Anonymous tries to access it
        with pytest.raises(ForbiddenError):
            await DialogRepository.get_or_create_dialog(
                session=test_session,
                dialog_id="user-thread-001",
                jwt_user_id=None
            )


class TestDialogRepositoryAuth:
    """Tests for authenticated user authorization"""

    @pytest.mark.asyncio
    async def test_user_can_access_own_dialog(self, test_session):
        """Logged-in user can access their own dialog"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        assert created is True
        assert dialog.user_id == "user_1"
        await test_session.commit()

        # Access again
        dialog2, created2 = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="user-thread-001",
            jwt_user_id="user_1"
        )
        assert created2 is False
        assert dialog2.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_user_cannot_access_other_user_dialog(self, test_session):
        """IDOR prevention: user cannot access another user's dialog"""
        # user_1 creates dialog
        await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="cross-user-thread",
            jwt_user_id="user_1"
        )
        await test_session.commit()

        # user_2 tries to access user_1's dialog
        with pytest.raises(ForbiddenError):
            await DialogRepository.get_or_create_dialog(
                session=test_session,
                dialog_id="cross-user-thread",
                jwt_user_id="user_2"
            )

    @pytest.mark.asyncio
    async def test_user_can_create_dialog_with_provided_id(self, test_session):
        """User can create dialog with specific ID (thread_id from frontend)"""
        dialog, created = await DialogRepository.get_or_create_dialog(
            session=test_session,
            dialog_id="custom-thread-uuid",
            jwt_user_id="user_1"
        )
        assert created is True
        assert dialog.id == "custom-thread-uuid"
        assert dialog.user_id == "user_1"

    @pytest.mark.asyncio
    async def test_list_user_dialogs_only_returns_own(self, test_session):
        """list_user_dialogs only returns dialogs for that specific user"""
        # Create dialogs for different users
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d1", jwt_user_id="user_1"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d2", jwt_user_id="user_1"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d3", jwt_user_id="user_2"
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="d4", jwt_user_id=None  # anonymous
        )
        await test_session.commit()

        # List for user_1
        dialogs = await DialogRepository.list_user_dialogs(
            session=test_session, user_id="user_1"
        )
        assert len(dialogs) == 2
        assert all(d.user_id == "user_1" for d in dialogs)

    @pytest.mark.asyncio
    async def test_list_anonymous_dialogs(self, test_session):
        """list_anonymous_dialogs only returns NULL user_id dialogs"""
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="a1", jwt_user_id=None
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="a2", jwt_user_id=None
        )
        await DialogRepository.get_or_create_dialog(
            session=test_session, dialog_id="u1", jwt_user_id="user_1"
        )
        await test_session.commit()

        dialogs = await DialogRepository.list_anonymous_dialogs(
            session=test_session
        )
        assert len(dialogs) == 2
        assert all(d.user_id is None for d in dialogs)
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd /home/luorome/software/CampusMind/backend
source .venv/bin/activate
pytest tests/services/test_dialog_repository.py -v
```

Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/services/test_dialog_repository.py
git commit -m "test(repo): add DialogRepository authorization tests"
```

---

## Chunk 3: API & Service Integration

### Task 5: Update completion.py — remove client user_id, use repository

**Files:**
- Modify: `app/api/v1/completion.py`

- [ ] **Step 1: Remove user_id from CompletionRequest**

In `CompletionRequest` (around line 67), remove:
```python
user_id: str = Field(default="system", description="User ID")
```

- [ ] **Step 2: Remove user_id from ChatRequest**

In `ChatRequest` (around line 444), remove:
```python
user_id: str = Field(default="system", description="User ID")
```

- [ ] **Step 3: Update get_or_create_dialog call in completion_stream**

The standalone `get_or_create_dialog` function (lines 154-185) should be replaced by calling `DialogRepository`. Update `completion_stream` (around line 328):

Change from:
```python
user_id = current_user.get("user_id") if current_user else None
# ...
dialog_id = get_or_create_dialog(
    session=db,
    dialog_id=request.dialog_id,
    user_id=request.user_id,
    agent_id=request.agent_id
)
```

To:
```python
from app.repositories.dialog_repository import DialogRepository

jwt_user_id = current_user.get("user_id") if current_user else None
# ...
dialog_id, _ = await DialogRepository.get_or_create_dialog(
    session=db,
    dialog_id=request.dialog_id,
    jwt_user_id=jwt_user_id,
    agent_id=request.agent_id
)
```

Also update `generate_stream` signature — remove `user_id` parameter since it's no longer needed in that function.

- [ ] **Step 4: Update completion endpoint (non-streaming)**

In `completion` endpoint (around line 375), make the same change — use `DialogRepository` instead of `get_or_create_dialog`.

- [ ] **Step 5: Update chat_stream endpoint**

Same pattern — use `DialogRepository`.

- [ ] **Step 6: Update chat endpoint**

Same pattern — use `DialogRepository`.

- [ ] **Step 7: Import DialogRepository at top of file**

Add:
```python
from app.repositories.dialog_repository import DialogRepository
```

- [ ] **Step 8: Run existing tests to ensure nothing is broken**

```bash
cd /home/luorome/software/CampusMind/backend
source .venv/bin/activate
pytest tests/api/test_completion.py -v
```

If tests fail due to missing `user_id` in request body, update test fixtures.

- [ ] **Step 9: Commit**

```bash
git add app/api/v1/completion.py
git commit -m "fix(api): use DialogRepository, remove client user_id, fix IDOR"
```

---

### Task 6: Update DialogService to support Optional[user_id]

**Files:**
- Modify: `app/services/dialog/dialog.py`

- [ ] **Step 1: Update create_dialog to accept Optional[user_id]**

Change `user_id: str` to `user_id: Optional[str]` in `create_dialog`.

Also update `list_user_dialogs` to document it only works for logged-in users (since anonymous dialogs don't have a user_id to query by).

- [ ] **Step 2: Commit**

```bash
git add app/services/dialog/dialog.py
git commit -m "refactor(service): DialogService supports nullable user_id"
```

---

### Task 7: Update database-onboarding.md to reflect schema changes

**Files:**
- Modify: `docs/database/database-onboarding.md`

- [ ] **Step 1: Document the new user_id NULLABLE behavior**

In section 3.2 "模型定义位置", update the note about Dialog to reflect that `user_id` is now optional.

- [ ] **Step 2: Commit**

```bash
git add docs/database/database-onboarding.md
git commit -m "docs(db): document nullable user_id in database-onboarding"
```

---

## Final: Run All Tests

```bash
cd /home/luorome/software/CampusMind/backend
source .venv/bin/activate
pytest tests/services/test_dialog.py tests/services/test_dialog_repository.py tests/api/test_completion.py -v
```

All tests should pass before declaring completion.

---

## Summary of Commits

1. `fix(db): make dialogs.user_id nullable, use FK SET NULL`
2. `feat(model): make Dialog.user_id nullable for anonymous support`
3. `feat(repo): add DialogRepository with authorization`
4. `test(repo): add DialogRepository authorization tests`
5. `fix(api): use DialogRepository, remove client user_id, fix IDOR`
6. `refactor(service): DialogService supports nullable user_id`
7. `docs(db): document nullable user_id in database-onboarding`
