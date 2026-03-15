"""
Completion API - Message with RAG integration
"""
from typing import List, Optional
from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field

from app.services.rag.handler import rag_handler


router = APIRouter(tags=["Completion"])


class CompletionRequest(BaseModel):
    """Request model for completion with RAG"""
    message: str = Field(..., description="User message/query")
    knowledge_ids: List[str] = Field(default=[], description="Knowledge base IDs for RAG")
    user_id: str = Field(default="system", description="User ID")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    enable_rag: bool = Field(default=True, description="Enable RAG retrieval")
    top_k: int = Field(default=5, description="Number of context chunks")
    min_score: float = Field(default=0.0, description="Minimum score threshold")


class CompletionResponse(BaseModel):
    """Response model for completion"""
    success: bool
    message: str = ""
    context: str = ""
    sources: List[dict] = []
    error: Optional[str] = None


@router.post("/completion", response_model=CompletionResponse)
async def completion(
    request: CompletionRequest,
):
    """
    Completion endpoint with RAG integration

    Minimal E2E flow:
    1. Receive user message
    2. If enable_rag and knowledge_ids provided, retrieve context
    3. Return message + context + sources

    Note: This is a minimal implementation that returns retrieved context.
    Full LLM generation would integrate with a chat model.
    """
    try:
        context = ""
        sources = []

        # RAG retrieval if enabled
        if request.enable_rag and request.knowledge_ids:
            result = await rag_handler.retrieve_with_sources(
                query=request.message,
                knowledge_ids=request.knowledge_ids,
                top_k=request.top_k,
                min_score=request.min_score
            )
            context = result["context"]
            sources = result["sources"]

        # For minimal implementation, we return the context
        # Full version would pass context to LLM for generation

        return CompletionResponse(
            success=True,
            message=request.message,
            context=context,
            sources=sources
        )

    except Exception as e:
        return CompletionResponse(
            success=False,
            message=request.message,
            error=str(e)
        )


class ChatRequest(BaseModel):
    """Simple chat request"""
    query: str = Field(..., description="User query")
    knowledge_id: str = Field(..., description="Single knowledge base ID")
    use_rag: bool = Field(default=True, description="Use RAG")


@router.post("/chat", response_model=CompletionResponse)
async def chat(
    request: ChatRequest,
):
    """
    Simple chat endpoint with RAG

    A simplified version of completion for single knowledge base
    """
    try:
        context = ""
        sources = []

        if request.use_rag:
            result = await rag_handler.retrieve_with_sources(
                query=request.query,
                knowledge_ids=[request.knowledge_id],
                top_k=5
            )
            context = result["context"]
            sources = result["sources"]

        return CompletionResponse(
            success=True,
            message=request.query,
            context=context,
            sources=sources
        )

    except Exception as e:
        return CompletionResponse(
            success=False,
            message=request.query,
            error=str(e)
        )
