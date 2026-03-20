"""
Tool Call Log Model - SQLModel for tool_call_logs table
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel
import uuid


class ToolCallStatus:
    """Tool call status constants"""
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ToolCallLog(SQLModel, table=True):
    """Tool call log table - records tool execution for analysis and debugging"""
    __tablename__ = "tool_call_logs"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True, description="Log ID (UUID)")
    dialog_id: Optional[str] = Field(default=None, index=True, description="Associated dialog ID")
    tool_name: str = Field(index=True, description="Tool name")
    user_id: Optional[str] = Field(default=None, index=True, description="User who triggered the call (None for anonymous)")
    status: str = Field(description="Status: success/failed/timeout")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    duration_ms: Optional[int] = Field(default=None, description="Execution duration in ms")
    created_at: datetime = Field(default_factory=datetime.now, description="Created time")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dialog_id": self.dialog_id,
            "tool_name": self.tool_name,
            "user_id": self.user_id,
            "status": self.status,
            "error_message": self.error_message,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
