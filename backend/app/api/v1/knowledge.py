"""
Knowledge API - Knowledge base management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.knowledge import KnowledgeService


router = APIRouter(tags=["Knowledge"])


class CreateKnowledgeRequest(BaseModel):
    """Request model for creating knowledge base"""
    name: str = Field(..., description="Knowledge base name")
    description: str = Field(default="", description="Knowledge base description")
    user_id: str = Field(default="system", description="User ID")


class KnowledgeResponse(BaseModel):
    """Response model for knowledge base"""
    id: str
    name: str
    description: str
    user_id: str
    create_time: Optional[str] = None
    update_time: Optional[str] = None


@router.post("/knowledge/create", response_model=KnowledgeResponse)
async def create_knowledge(
    request: CreateKnowledgeRequest,
):
    """Create a new knowledge base"""
    try:
        knowledge = KnowledgeService.create_knowledge(
            name=request.name,
            user_id=request.user_id,
            description=request.description,
        )
        return KnowledgeResponse(**knowledge.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(knowledge_id: str):
    """Get knowledge base by ID"""
    knowledge = KnowledgeService.get_knowledge(knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return KnowledgeResponse(**knowledge.to_dict())


@router.get("/users/{user_id}/knowledge", response_model=List[KnowledgeResponse])
async def list_user_knowledge(user_id: str):
    """List all knowledge bases for a user"""
    knowledge_list = KnowledgeService.list_knowledge_by_user(user_id)
    return [KnowledgeResponse(**k.to_dict()) for k in knowledge_list]


@router.delete("/knowledge/{knowledge_id}")
async def delete_knowledge(knowledge_id: str):
    """Delete a knowledge base"""
    success = KnowledgeService.delete_knowledge(knowledge_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return {"success": True}
