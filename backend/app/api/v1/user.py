"""
User API - User profile management endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.repositories.user_repository import UserRepository
from app.api.dependencies import get_current_user
from app.database.session import async_session_maker


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
