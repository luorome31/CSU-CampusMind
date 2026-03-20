"""
Dialog Model - SQLModel for dialog (conversation) table
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Dialog(SQLModel, table=True):
    """
    Dialog table - stores conversation metadata

    Fields:
    - id: Conversation unique UUID
    - user_id: User identifier
    - agent_id: Agent template ID used
    - updated_at: Last interaction time
    """
    __tablename__ = "dialog"

    id: str = Field(default=None, primary_key=True, description="Dialog ID (UUID)")
    user_id: Optional[str] = Field(default=None, index=True, description="User ID (NULL for anonymous)")
    agent_id: Optional[str] = Field(default=None, index=True, description="Agent template ID")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "agent_id": self.agent_id,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
