"""
Chat History Model - SQLModel for chat_history table
"""
from datetime import datetime
from typing import Optional, Any
from sqlmodel import Field, SQLModel, JSON


class ChatHistory(SQLModel, table=True):
    """
    Chat history table - stores each message in a conversation

    Fields:
    - id: Message unique UUID
    - dialog_id: Associated dialog ID
    - role: user / assistant / system
    - content: Message text content
    - file_url: Optional attachment/image URL
    - events: Tool call details (START/END status) for display
    - extra: Performance data (token consumption, duration, model name)
    - created_at: Creation time (for ordering)
    """
    __tablename__ = "chat_history"

    id: str = Field(default=None, primary_key=True, description="Message ID (UUID)")
    dialog_id: str = Field(index=True, description="Dialog ID")
    role: str = Field(description="Role: user/assistant/system")
    content: str = Field(description="Message content")
    file_url: Optional[str] = Field(default=None, description="Attachment URL")
    events: Optional[str] = Field(default=None, description="Tool call events (JSON string)")
    extra: Optional[str] = Field(default=None, description="Extra data like metadata (JSON string)")
    created_at: datetime = Field(default_factory=datetime.now, description="Create time")

    def to_dict(self):
        return {
            "id": self.id,
            "dialog_id": self.dialog_id,
            "role": self.role,
            "content": self.content,
            "file_url": self.file_url,
            "events": self.events,
            "extra": self.extra,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
