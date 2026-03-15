"""
Database Session Management
"""
from typing import AsyncGenerator
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool


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


from pydantic import BaseModel
