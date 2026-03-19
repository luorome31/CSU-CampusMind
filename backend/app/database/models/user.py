"""
User Model - SQLModel for users table
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User table - stores CAS authenticated users"""
    __tablename__ = "users"

    id: str = Field(primary_key=True, description="User ID (CAS username/student ID)")
    username: str = Field(unique=True, index=True, description="Unique username")
    display_name: Optional[str] = Field(default=None, description="Display name")
    avatar_url: Optional[str] = Field(default=None, description="Avatar URL")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone number")
    is_active: bool = Field(default=True, description="Account status")
    created_at: datetime = Field(default_factory=datetime.now, description="Created time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Updated time")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "email": self.email,
            "phone": self.phone,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
