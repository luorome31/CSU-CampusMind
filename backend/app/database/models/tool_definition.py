"""
Tool Definition Model - SQLModel for tool_definitions table
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel


class ToolDefinition(SQLModel, table=True):
    """Tool definition table - stores available tools metadata"""
    __tablename__ = "tool_definitions"

    id: str = Field(primary_key=True, description="Tool ID")
    name: str = Field(unique=True, index=True, description="Tool name")
    description: Optional[str] = Field(default=None, description="Tool description")
    category: Optional[str] = Field(default=None, index=True, description="Tool category: library/career/jwc/oa/rag")
    requires_auth: bool = Field(default=False, description="Requires authentication")
    created_at: datetime = Field(default_factory=datetime.now, description="Created time")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "requires_auth": self.requires_auth,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
