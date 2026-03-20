"""
Retrieve API - RAG retrieval endpoints
"""
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.services.rag.handler import rag_handler


router = APIRouter(tags=["Retrieve"])


class RetrieveRequest(BaseModel):
    """Request model for retrieval"""
    query: str = Field(..., description="User query")
    knowledge_ids: List[str] = Field(..., description="List of knowledge base IDs")
    enable_vector: bool = Field(default=True, description="Enable vector search")
    enable_keyword: bool = Field(default=True, description="Enable keyword search")
    top_k: int = Field(default=5, description="Number of results to return")
    min_score: float = Field(default=0.0, description="Minimum score threshold")


class RetrieveResponse(BaseModel):
    """Response model for retrieval"""
    success: bool
    context: str = ""
    sources: List[dict] = []
    error: Optional[str] = None


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(
    request: RetrieveRequest,
):
    """
    RAG retrieval endpoint

    Performs hybrid retrieval from ChromaDB (vector) and Elasticsearch (keyword),
    returns context for LLM generation.
    """
    try:
        result = await rag_handler.retrieve_with_sources(
            query=request.query,
            knowledge_ids=request.knowledge_ids,
            enable_vector=request.enable_vector,
            enable_keyword=request.enable_keyword,
            top_k=request.top_k,
            min_score=request.min_score
        )

        return RetrieveResponse(
            success=True,
            context=result["context"],
            sources=result["sources"]
        )

    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return RetrieveResponse(
            success=False,
            error=str(e)
        )


from loguru import logger
