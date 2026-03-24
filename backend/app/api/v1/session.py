"""
Session API - Active session management endpoints for Personal Center
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

from app.api.dependencies import get_current_user
from app.core.session.session_tracker import (
    get_user_sessions,
    get_session_by_id,
    delete_session,
    delete_all_sessions,
)


router = APIRouter(prefix="/auth/sessions", tags=["Session"])


class SessionResponse(BaseModel):
    """Response model for a session"""
    session_id: str
    device: str
    location: str
    created_at: float
    is_current: bool


class CurrentSessionResponse(BaseModel):
    """Response model for current session info"""
    session_id: str
    device: str
    location: str
    created_at: float


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    List all active sessions for the current user.
    Identifies current session from X-Session-ID header or falls back to User-Agent fingerprinting.
    """
    user_id = current_user["user_id"]
    sessions = await get_user_sessions(user_id)

    # Get current session ID from header (set by frontend)
    current_session_id = request.headers.get("X-Session-ID", "")

    # If no session ID header, try to match by User-Agent
    if not current_session_id:
        user_agent = request.headers.get("user-agent", "")
        for session in sessions:
            if session.user_agent == user_agent:
                current_session_id = session.session_id
                break

    return [
        SessionResponse(
            session_id=s.session_id,
            device=s.device,
            location=s.location,
            created_at=s.created_at,
            is_current=(s.session_id == current_session_id),
        )
        for s in sessions
    ]


@router.get("/current", response_model=Optional[CurrentSessionResponse])
async def get_current_session(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get current session information.
    """
    user_id = current_user["user_id"]
    current_session_id = request.headers.get("X-Session-ID", "")

    if current_session_id:
        session = await get_session_by_id(user_id, current_session_id)
        if session:
            return CurrentSessionResponse(
                session_id=session.session_id,
                device=session.device,
                location=session.location,
                created_at=session.created_at,
            )

    # Fallback: match by User-Agent
    user_agent = request.headers.get("user-agent", "")
    sessions = await get_user_sessions(user_id)
    for session in sessions:
        if session.user_agent == user_agent:
            return CurrentSessionResponse(
                session_id=session.session_id,
                device=session.device,
                location=session.location,
                created_at=session.created_at,
            )

    return None


@router.delete("/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke a specific session.
    """
    user_id = current_user["user_id"]
    success = await delete_session(user_id, session_id)

    if not success:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True, "message": "Session revoked"}


@router.delete("")
async def revoke_all_sessions(
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke all sessions except the current one.
    """
    user_id = current_user["user_id"]
    count = await delete_all_sessions(user_id)

    return {"success": True, "message": f"{count} sessions revoked"}
