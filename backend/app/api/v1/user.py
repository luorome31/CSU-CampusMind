"""
User API - User profile management endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select, func

from app.repositories.user_repository import UserRepository
from app.api.dependencies import get_current_user
from app.database.session import async_session_maker
from app.database.models import Dialog, ChatHistory, KnowledgeBase


router = APIRouter(prefix="/users", tags=["User"])


class UserProfileResponse(BaseModel):
    id: str
    username: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]


class UpdateProfileRequest(BaseModel):
    display_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class UsageStatsResponse(BaseModel):
    conversation_count: int
    message_count: int
    knowledge_base_count: int
    join_date: str


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    user_id = current_user["user_id"]
    async with async_session_maker() as session:
        user = await UserRepository.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfileResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )


@router.patch("/me", response_model=UserProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile."""
    user_id = current_user["user_id"]
    async with async_session_maker() as session:
        user = await UserRepository.update(
            session,
            user_id,
            display_name=request.display_name,
            email=request.email,
            phone=request.phone,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserProfileResponse(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            avatar_url=user.avatar_url,
            email=user.email,
            phone=user.phone,
            is_active=user.is_active,
            created_at=user.created_at.isoformat() if user.created_at else None,
            updated_at=user.updated_at.isoformat() if user.updated_at else None,
        )


@router.get("/me/stats", response_model=UsageStatsResponse)
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get current user's usage statistics."""
    user_id = current_user["user_id"]
    async with async_session_maker() as session:
        # Get user for join date
        user = await UserRepository.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Count conversations
        conv_count = await session.scalar(
            select(func.count()).select_from(Dialog).where(Dialog.user_id == user_id)
        )

        # Count messages (via dialog join)
        msg_count = await session.scalar(
            select(func.count())
            .select_from(ChatHistory)
            .join(Dialog, ChatHistory.dialog_id == Dialog.id)
            .where(Dialog.user_id == user_id)
        )

        # Count knowledge bases
        kb_count = await session.scalar(
            select(func.count()).select_from(KnowledgeBase).where(KnowledgeBase.user_id == user_id)
        )

        return UsageStatsResponse(
            conversation_count=conv_count or 0,
            message_count=msg_count or 0,
            knowledge_base_count=kb_count or 0,
            join_date=user.created_at.strftime("%Y-%m") if user.created_at else "",
        )
