"""
Knowledge Base Model - SQLModel for knowledge table
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class KnowledgeBase(SQLModel, table=True):
    """Knowledge base table"""
    __tablename__ = "knowledge"

    id: str = Field(default=None, primary_key=True, description="Knowledge base ID (prefix: t_)")
    name: str = Field(default=None, unique=True, index=True, description="Knowledge base name")
    description: Optional[str] = Field(default="", description="Knowledge base description")
    user_id: str = Field(index=True, description="Creator user ID")
    create_time: datetime = Field(default_factory=datetime.now, description="Create time")
    update_time: datetime = Field(default_factory=datetime.now, description="Update time")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "update_time": self.update_time.isoformat() if self.update_time else None,
        }
