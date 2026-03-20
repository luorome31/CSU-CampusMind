# Database Init on Startup — Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three database integration issues: (1) `create_db_and_tables()` not called on startup, (2) hardcoded SQLite URL ignoring environment config, (3) incomplete model imports.

**Architecture:** Refactor `app/database/session.py` to use `settings.database_url` (already reads from `DATABASE_URL` env var), wire `create_db_and_tables()` into FastAPI startup lifecycle via `app/main.py`, and complete all model imports in `create_db_and_tables()`.

**Tech Stack:** FastAPI, SQLModel, SQLAlchemy, Pydantic BaseSettings, loguru

---

## Chunk 1: Refactor session.py to use environment-configured database URL

**Files:**
- Modify: `backend/app/database/session.py`

**Context:** `session.py` currently hardcodes `DATABASE_URL = "sqlite:///./campusmind.db"` and ignores `DatabaseConfig` and `settings.database_url`. The app already has a proper config system in `app/config.py` that reads `DATABASE_URL` from environment with a sensible default. We will use that instead.

- [ ] **Step 1: Read the current session.py**

```python
"""
Database Session Management
"""
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from pydantic import BaseModel


class DatabaseConfig(BaseModel):
    """Database configuration"""
    url: str = "postgresql://postgres:postgres@localhost:5432/campusmind"
    echo: bool = False


# SQLite for demo (use PostgreSQL in production)
DATABASE_URL = "sqlite:///./campusmind.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_db_and_tables():
    """Create all tables"""
    from app.database.models.knowledge import KnowledgeBase
    from app.database.models.knowledge_file import KnowledgeFile
    from app.database.models.dialog import Dialog
    from app.database.models.chat_history import ChatHistory
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Get database session"""
    with Session(engine) as session:
        yield session
```

- [ ] **Step 2: Replace session.py content**

```python
"""
Database Session Management

Database URL is driven by DATABASE_URL environment variable (default: sqlite:///./campusmind.db).
For production, set DATABASE_URL=postgresql://user:pass@host:5432/dbname.
"""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool, QueuePool

from app.config import settings


def _build_engine():
    """Create SQLAlchemy engine based on DATABASE_URL."""
    url = settings.database_url
    is_sqlite = url.startswith("sqlite")

    if is_sqlite:
        # SQLite: use StaticPool for in-process single connection, create DB file if not exists
        return create_engine(
            url,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL (or other DB): use QueuePool for connection pooling
        return create_engine(
            url,
            echo=False,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
        )


engine = _build_engine()


def create_db_and_tables():
    """Create all tables registered in SQLModel.metadata.

    Call this once on application startup. Safe to call multiple times
    (uses CREATE TABLE IF NOT EXISTS).
    """
    # Import all models to ensure they are registered with SQLModel.metadata
    from app.database.models import (
        Dialog,
        ChatHistory,
        KnowledgeBase,
        KnowledgeFile,
        User,
        ToolDefinition,
        ToolCallLog,
    )
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a database session. Usage: `with get_session() as session: ...`"""
    with Session(engine) as session:
        yield session


# Alias for FastAPI Depends compatibility
def session_dependency() -> Generator[Session, None, None]:
    """FastAPI dependency for database session."""
    with Session(engine) as session:
        yield session
```

- [ ] **Step 3: Verify the file was updated correctly**

Run: `cat backend/app/database/session.py`
Expected: Content matches the above

- [ ] **Step 4: Commit**

```bash
git add backend/app/database/session.py
git commit -m "refactor(db): use settings.database_url instead of hardcoded SQLite URL"
```

---

## Chunk 2: Call create_db_and_tables() in main.py startup

**Files:**
- Modify: `backend/app/main.py`

**Context:** Currently `main.py` never calls `create_db_and_tables()`, so on a fresh database the tables are never created. We need to add a lifespan context manager (FastAPI's modern approach) or an `@app.on_event("startup")` hook to call it. We use lifespan for FastAPI 0.100+.

- [ ] **Step 1: Read current main.py**

```python
"""
CampusMind Backend Application
"""
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Configure loguru for uvicorn - output to stdout
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
        }
    ]
)

from app.api.v1 import crawl, index, knowledge, knowledge_file, retrieve, completion, auth


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CampusMind API",
        description="CampusMind - AI-powered campus assistant",
        version="0.1.0",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(crawl.router, prefix="/api/v1")
    app.include_router(index.router, prefix="/api/v1")
    app.include_router(knowledge.router, prefix="/api/v1")
    app.include_router(knowledge_file.router, prefix="/api/v1")
    app.include_router(retrieve.router, prefix="/api/v1")
    app.include_router(completion.router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 2: Replace main.py with lifespan-based startup logic**

```python
"""
CampusMind Backend Application
"""
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Configure loguru for uvicorn - output to stdout
logger.configure(
    handlers=[
        {
            "sink": sys.stdout,
            "level": "INFO",
            "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name} | {message}",
        }
    ]
)

from app.api.v1 import crawl, index, knowledge, knowledge_file, retrieve, completion, auth
from app.database.session import create_db_and_tables
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: run startup and shutdown logic."""
    logger.info("Initializing database tables...")
    create_db_and_tables()
    logger.info(f"Database initialized: {settings.database_url}")
    yield
    logger.info("Shutting down...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CampusMind API",
        description="CampusMind - AI-powered campus assistant",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(crawl.router, prefix="/api/v1")
    app.include_router(index.router, prefix="/api/v1")
    app.include_router(knowledge.router, prefix="/api/v1")
    app.include_router(knowledge_file.router, prefix="/api/v1")
    app.include_router(retrieve.router, prefix="/api/v1")
    app.include_router(completion.router, prefix="/api/v1")

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

- [ ] **Step 3: Verify the file was updated correctly**

Run: `cat backend/app/main.py`
Expected: Content matches the above

- [ ] **Step 4: Commit**

```bash
git add backend/app/main.py
git commit -m "feat(db): call create_db_and_tables() on FastAPI startup"
```

---

## Chunk 3: Update completion.py to use the centralized session dependency

**Files:**
- Modify: `backend/app/api/v1/completion.py:34-37`

**Context:** `completion.py` defines its own local `get_db_session()` instead of importing from `app.database.session`. After refactoring `session.py`, we can remove the duplicate and import the centralized one. This ensures all API routes use the same engine configuration.

- [ ] **Step 1: Verify current duplicate in completion.py (lines 34-37)**

```python
def get_db_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
```

- [ ] **Step 2: Remove the duplicate get_db_session from completion.py, import session_dependency instead**

Replace lines 16 and 34-37 in `backend/app/api/v1/completion.py`:

Old (line 16):
```python
from app.database.session import engine
```

New (line 16):
```python
from app.database.session import session_dependency
```

Old (lines 34-37):
```python
def get_db_session():
    """Get database session"""
    with Session(engine) as session:
        yield session
```

New (replace with import alias):
```python
# Re-export for backwards compatibility with existing Depends() calls
get_db_session = session_dependency
```

- [ ] **Step 3: Verify the edit was applied correctly**

Run: `grep -n "get_db_session\|session_dependency\|from app.database.session" backend/app/api/v1/completion.py`
Expected:
- Line with `from app.database.session import session_dependency`
- Line with `get_db_session = session_dependency`

- [ ] **Step 4: Commit**

```bash
git add backend/app/api/v1/completion.py
git commit -m "refactor(db): deduplicate get_db_session, use centralized session_dependency"
```

---

## Chunk 4: Run tests to verify the fix

**Files:**
- Run: existing tests

**Context:** After the refactor, run the existing test suite to ensure nothing is broken.

- [ ] **Step 1: Run all unit tests in tests/services/**

Run: `cd backend && uv run pytest tests/services/ -v 2>&1 | tail -40`
Expected: All tests pass (or pre-existing failures unrelated to this change)

- [ ] **Step 2: Run a quick import smoke test**

Run: `cd backend && uv run python -c "from app.main import app; from app.database.session import engine, create_db_and_tables, session_dependency; print('OK')"`
Expected: Output `OK` with no errors

- [ ] **Step 3: Verify startup logs show database init**

Run: `cd backend && uv run timeout 3 python -c "from app.main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=18000, log_level='info')" 2>&1 | grep -i "database\|table"`
Expected: Log lines containing "Initializing database tables" and "Database initialized"

- [ ] **Step 4: Commit (if tests pass)**

```bash
git add backend/
git commit -m "test(db): add database init verification to test suite"
```

---

## Chunk 5: Update docs to reflect the fix

**Files:**
- Modify: `docs/database/database-onboarding.md`

**Context:** The onboarding doc mentions "问题 3: `create_db_and_tables()` 不完整" as a known issue. After fixing, update the status.

- [ ] **Step 1: Update database-onboarding.md — mark issue 3 as resolved**

Find and update section 3.2 (中优先级), 问题 3:

Old text:
```
**问题 3: `create_db_and_tables()` 不完整**

- **现状:** 主应用启动时从未调用建表函数，只在测试中调用
- **位置:** `app/database/session.py`
- **修复方向:** 在 `app/main.py` 启动时调用
```

New text:
```
**问题 3: `create_db_and_tables()` 不完整** ✅ 已修复

- **修复:** 在 `app/main.py` 的 lifespan 中调用 `create_db_and_tables()`，
  所有模型 (User, ToolDefinition, ToolCallLog) 均已导入
- **位置:** `app/main.py`, `app/database/session.py`
```

- [ ] **Step 2: Commit**

```bash
git add docs/database/database-onboarding.md
git commit -m "docs(db): mark issue 3 as resolved in database-onboarding.md"
```
