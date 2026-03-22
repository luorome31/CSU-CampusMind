"""
Index API - Offline indexing endpoints
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.rag.indexer import indexer
from app.services.storage.client import storage_client


router = APIRouter(tags=["Index"])


class IndexRequest(BaseModel):
    """Request model for indexing"""
    content: str = Field(..., description="Content to index")
    knowledge_id: str = Field(..., description="Knowledge base ID")
    source_name: str = Field(default="text", description="Source name/file name")
    enable_vector: bool = Field(default=True, description="Enable vector storage")
    enable_keyword: bool = Field(default=True, description="Enable keyword storage")


class IndexFromOssRequest(BaseModel):
    """Request model for indexing from OSS"""
    oss_url: str = Field(..., description="OSS URL of the content file")
    knowledge_id: str = Field(..., description="Knowledge base ID")
    enable_vector: bool = Field(default=True, description="Enable vector storage")
    enable_keyword: bool = Field(default=True, description="Enable keyword storage")


class IndexResponse(BaseModel):
    """Response model for indexing"""
    success: bool
    chunk_count: int = 0
    file_id: Optional[str] = None
    knowledge_id: Optional[str] = None
    error: Optional[str] = None


@router.post("/index/create", response_model=IndexResponse)
async def create_index(
    request: IndexRequest,
):
    """
    Index content to vector DB and/or keyword DB

    The content will be chunked and stored to both ChromaDB (vector)
    and Elasticsearch (keyword) based on the flags.
    """
    try:
        result = await indexer.index_content(
            content=request.content,
            knowledge_id=request.knowledge_id,
            source_name=request.source_name,
            metadata={"enable_vector": request.enable_vector, "enable_keyword": request.enable_keyword}
        )

        return IndexResponse(
            success=result.get("success", False),
            chunk_count=result.get("chunk_count", 0),
            file_id=result.get("file_id"),
            knowledge_id=request.knowledge_id,
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index/create-from-oss", response_model=IndexResponse)
async def index_from_oss(
    request: IndexFromOssRequest,
):
    """
    Index content from OSS storage

    Downloads content from OSS, chunks it, and stores to ChromaDB
    and/or Elasticsearch.
    """
    try:
        result = await indexer.index_from_oss(
            oss_url=request.oss_url,
            knowledge_id=request.knowledge_id,
            storage_client=storage_client
        )

        return IndexResponse(
            success=result.get("success", False),
            chunk_count=result.get("chunk_count", 0),
            file_id=result.get("file_id"),
            knowledge_id=request.knowledge_id,
            error=result.get("error")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
