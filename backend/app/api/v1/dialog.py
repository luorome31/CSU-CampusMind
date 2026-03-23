"""
Dialog API - Conversation session management
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_dependency
from app.repositories.dialog_repository import DialogRepository
from app.api.dependencies import get_optional_user

router = APIRouter(tags=["Dialog"])


class DialogResponse(BaseModel):
    """Response model for dialog/session"""
    id: str
    user_id: Optional[str]
    agent_id: Optional[str]
    title: Optional[str]
    updated_at: str


class ChatMessageResponse(BaseModel):
    """Response model for chat history message"""
    id: str
    role: str
    content: str
    file_url: Optional[str] = None
    events: Optional[str] = None
    created_at: str


class UpdateDialogRequest(BaseModel):
    """Request model for updating dialog"""
    title: str = Field(..., description="New title for the conversation")


@router.get("/dialogs", response_model=List[DialogResponse])
async def list_dialogs(
    limit: int = 50,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency)
):
    """List all conversations for the current user"""
    user_id = current_user.get("user_id") if current_user else None
    
    if user_id:
        dialogs = await DialogRepository.list_user_dialogs(db, user_id, limit=limit)
    else:
        dialogs = await DialogRepository.list_anonymous_dialogs(db, limit=limit)
        
    return [DialogResponse(**d.to_dict()) for d in dialogs]


@router.get("/dialogs/{dialog_id}/messages", response_model=List[ChatMessageResponse])
async def get_dialog_messages(
    dialog_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency)
):
    """Retrieve full message history for a specific conversation"""
    user_id = current_user.get("user_id") if current_user else None
    messages = await DialogRepository.get_dialog_history(db, dialog_id, user_id)
    
    if not messages and not await DialogRepository.get_dialog_if_authorized(db, dialog_id, user_id):
        raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
    return [ChatMessageResponse(**m.to_dict()) for m in messages]


@router.patch("/dialogs/{dialog_id}", response_model=DialogResponse)
async def update_dialog(
    dialog_id: str,
    request: UpdateDialogRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency)
):
    """Update conversation metadata (e.g., rename title)"""
    user_id = current_user.get("user_id") if current_user else None
    dialog = await DialogRepository.update_dialog_title(db, dialog_id, request.title, user_id)
    
    if not dialog:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
    return DialogResponse(**dialog.to_dict())


@router.delete("/dialogs/{dialog_id}")
async def delete_dialog(
    dialog_id: str,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency)
):
    """Delete a conversation and its history"""
    user_id = current_user.get("user_id") if current_user else None
    success = await DialogRepository.delete_dialog(db, dialog_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found or access denied")
        
    return {"success": True, "message": "Conversation deleted"}
