"""
Database Session Management

Database URL is driven by DATABASE_URL environment variable (default: sqlite:///./campusmind.db).
For production, set DATABASE_URL=postgresql://user:pass@host:5432/dbname.
"""
from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

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


def _build_async_engine():
    """Create async SQLAlchemy engine based on DATABASE_URL."""
    url = settings.database_url
    is_sqlite = url.startswith("sqlite")

    # Convert sync URL to async URL
    if url.startswith("sqlite"):
        async_url = url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif url.startswith("postgresql"):
        async_url = url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        async_url = url

    if is_sqlite:
        # SQLite: use StaticPool for in-process single connection
        return create_async_engine(
            async_url,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        # PostgreSQL (or other DB): async engine handles pooling internally via asyncpg
        return create_async_engine(
            async_url,
            echo=False,
        )


engine = _build_engine()
async_engine = _build_async_engine()

# Async session maker
async_session_maker = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


def create_db_and_tables():
    """Create all tables registered in SQLModel.metadata.

    Call this once on application startup. Safe to call multiple times
    (uses CREATE TABLE IF NOT EXISTS).
    """
    # Import all models to ensure they are registered with SQLModel.metadata
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


async def async_session_dependency() -> AsyncSession:
    """FastAPI dependency for async database session."""
    async with async_session_maker() as session:
        yield session
