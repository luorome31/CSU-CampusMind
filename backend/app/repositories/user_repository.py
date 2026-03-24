"""
User Repository - User profile access with authorization.
"""
from datetime import datetime
from typing import Optional
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.user import User


class UserRepository:
    """Repository for user profile operations."""

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID."""
        statement = select(User).where(User.id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(
        session: AsyncSession,
        user_id: str,
        display_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile fields."""
        user = await UserRepository.get_by_id(session, user_id)
        if not user:
            return None

        if display_name is not None:
            user.display_name = display_name
        if email is not None:
            user.email = email
        if phone is not None:
            user.phone = phone

        user.updated_at = datetime.now()
        await session.commit()
        await session.refresh(user)
        return user
