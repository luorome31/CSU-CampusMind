"""
Knowledge File API - Knowledge file management endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.knowledge_file import KnowledgeFileService
from app.services.storage.client import storage_client
from app.database.models.knowledge_file import FileStatus, KnowledgeFile
from app.database.session import engine
from sqlmodel import Session, select
from datetime import datetime


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


class UpdateContentRequest(BaseModel):
    """Request model for modifying raw markdown content"""
    content: str = Field(..., description="Markdown content to save")


class TriggerIndexRequest(BaseModel):
    """Request model for triggering manual indexing"""
    enable_vector: bool = True
    enable_keyword: bool = True


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


@router.get("/knowledge_file/{file_id}/content", response_model=str)
async def get_knowledge_file_content(file_id: str):
    """Get the raw markdown content of a knowledge file"""
    knowledge_file = KnowledgeFileService.get_knowledge_file(file_id)
    if not knowledge_file:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
        
    object_name = "/".join(knowledge_file.oss_url.split("/")[-2:])
    try:
        content = storage_client.get_content(object_name)
        return content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch content: {str(e)}")


@router.put("/knowledge_file/{file_id}/content")
async def update_knowledge_file_content(
    file_id: str,
    request: UpdateContentRequest,
):
    """Update the raw markdown content of a knowledge file"""
    knowledge_file = KnowledgeFileService.get_knowledge_file(file_id)
    if not knowledge_file:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
        
    object_name = "/".join(knowledge_file.oss_url.split("/")[-2:])
    content_bytes = request.content.encode("utf-8")
    
    try:
        storage_client.upload_content(object_name, content_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update stored content: {str(e)}")
        
    with Session(engine) as session:
        statement = select(KnowledgeFile).where(KnowledgeFile.id == file_id)
        db_file = session.exec(statement).first()
        if db_file:
            db_file.file_size = len(content_bytes)
            db_file.status = FileStatus.VERIFIED
            db_file.update_time = datetime.now()
            session.commit()
            
    return {"success": True, "message": "Content updated and file verified"}


@router.post("/knowledge_file/{file_id}/trigger_index")
async def trigger_knowledge_file_index(
    file_id: str,
    request: TriggerIndexRequest,
):
    """Trigger manual indexing for a verified knowledge file"""
    knowledge_file = KnowledgeFileService.get_knowledge_file(file_id)
    if not knowledge_file:
        raise HTTPException(status_code=404, detail="Knowledge file not found")
        
    if knowledge_file.status not in [FileStatus.VERIFIED, FileStatus.SUCCESS, FileStatus.PENDING_VERIFY]:
        raise HTTPException(status_code=400, detail="File is not ready for indexing")
        
    KnowledgeFileService.update_file_status(file_id, FileStatus.INDEXING)
    
    object_name = "/".join(knowledge_file.oss_url.split("/")[-2:])
    try:
        content_bytes = storage_client.get_content(object_name)
        content_str = content_bytes.decode("utf-8")
    except Exception as e:
        KnowledgeFileService.update_file_status(file_id, FileStatus.FAIL)
        raise HTTPException(status_code=500, detail=f"Failed to fetch content for indexing: {str(e)}")
        
    from app.services.rag.indexer import indexer
    try:
        index_result = await indexer.index_content(
            content=content_str,
            knowledge_id=knowledge_file.knowledge_id,
            source_name=knowledge_file.file_name,
            metadata={
                "file_id": file_id,
                "enable_vector": request.enable_vector,
                "enable_keyword": request.enable_keyword,
            }
        )
        
        if index_result.get("success"):
            KnowledgeFileService.update_file_status(file_id, FileStatus.INDEXED)
            return {"success": True, "message": "File indexed successfully"}
        else:
            KnowledgeFileService.update_file_status(file_id, FileStatus.FAIL)
            raise HTTPException(status_code=500, detail=index_result.get("error", "Indexing failed"))
            
    except Exception as e:
        KnowledgeFileService.update_file_status(file_id, FileStatus.FAIL)
        raise HTTPException(status_code=500, detail=str(e))
