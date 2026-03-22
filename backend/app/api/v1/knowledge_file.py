"""
Knowledge File API - Knowledge file management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.knowledge_file import KnowledgeFileService


router = APIRouter(tags=["Knowledge-File"])


class CreateKnowledgeFileRequest(BaseModel):
    """Request model for creating knowledge file"""
    file_name: str = Field(..., description="File name")
    knowledge_id: str = Field(..., description="Knowledge base ID")
    user_id: str = Field(default="system", description="User ID")
    oss_url: str = Field(..., description="OSS/MinIO URL")
    file_size: int = Field(default=0, description="File size in bytes")


class KnowledgeFileResponse(BaseModel):
    """Response model for knowledge file"""
    id: str
    file_name: str
    knowledge_id: str
    user_id: str
    status: str
    oss_url: str
    file_size: int
    create_time: Optional[str] = None
    update_time: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    """Request model for updating file status"""
    status: str = Field(..., description="New status: success/process/fail")


@router.post("/knowledge_file/create", response_model=KnowledgeFileResponse)
async def create_knowledge_file(
    request: CreateKnowledgeFileRequest,
):
    """Create a new knowledge file record"""
    try:
        knowledge_file = KnowledgeFileService.create_knowledge_file(
            file_name=request.file_name,
            knowledge_id=request.knowledge_id,
            user_id=request.user_id,
            oss_url=request.oss_url,
            file_size=request.file_size,
        )
        return KnowledgeFileResponse(**knowledge_file.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge_file/{file_id}", response_model=KnowledgeFileResponse)
async def get_knowledge_file(file_id: str):
    """Get knowledge file by ID"""
    knowledge_file = KnowledgeFileService.get_knowledge_file(file_id)
    if not knowledge_file:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    return KnowledgeFileResponse(**knowledge_file.to_dict())


@router.get("/knowledge/{knowledge_id}/files", response_model=List[KnowledgeFileResponse])
async def list_knowledge_files(knowledge_id: str):
    """List all files in a knowledge base"""
    files = KnowledgeFileService.list_knowledge_files(knowledge_id)
    return [KnowledgeFileResponse(**f.to_dict()) for f in files]


@router.patch("/knowledge_file/{file_id}")
async def update_knowledge_file_status(
    file_id: str,
    request: UpdateStatusRequest,
):
    """Update file processing status"""
    success = KnowledgeFileService.update_file_status(file_id, request.status)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    return {"success": True}


@router.delete("/knowledge_file/{file_id}")
async def delete_knowledge_file(file_id: str):
    """Delete a knowledge file"""
    success = KnowledgeFileService.delete_knowledge_file(file_id)
    if not success:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
    return {"success": True}
