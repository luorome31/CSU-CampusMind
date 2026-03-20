"""
Completion API - Message with RAG integration and LLM streaming
"""
import json
import time
from typing import List, Optional, Callable, AsyncGenerator
from starlette.types import Receive
from fastapi import APIRouter, Body, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

# Use model from settings as default
from app.database.session import async_session_dependency
from app.database.models import Dialog, ChatHistory
from app.services.rag.handler import rag_handler
from app.core.agents.react_agent import ReactAgent, StreamOutput
from app.core.tools.rag_tool import create_rag_tool

# Import authentication dependency
from app.api.dependencies import get_optional_user, get_redis_client
from app.core.agents.factory import get_agent_factory, initialize_agent_factory
from app.core.session.factory import get_session_manager

# Import LangChain OpenAI
from langchain_openai import ChatOpenAI

# Import DialogRepository for secure dialog access
from app.repositories.dialog_repository import DialogRepository
from app.services.history.cache import HistoryCacheService

from redis.asyncio import Redis


router = APIRouter(tags=["Completion"])


# Re-export for backwards compatibility with existing Depends() calls
get_db_session = async_session_dependency


async def get_history_cache_service(
    redis: Redis = Depends(get_redis_client),
) -> HistoryCacheService:
    """FastAPI dependency for HistoryCacheService."""
    return HistoryCacheService(redis=redis)


class WatchedStreamingResponse(StreamingResponse):
    """
    Override StreamingResponse to support pause during streaming
    """
    def __init__(
        self,
        content,
        callback: Callable = None,
        status_code: int = 200,
        headers=None,
        media_type: str | None = None,
        background=None,
    ):
        super().__init__(content, status_code, headers, media_type, background)
        self.callback = callback

    async def listen_for_disconnect(self, receive: Receive) -> None:
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                if self.callback:
                    self.callback()
                break


class CompletionRequest(BaseModel):
    """Request model for completion with RAG"""
    message: str = Field(..., description="User message/query")
    knowledge_ids: List[str] = Field(default=[], description="Knowledge base IDs for RAG")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    dialog_id: Optional[str] = Field(default=None, description="Dialog ID (for history)")
    enable_rag: bool = Field(default=True, description="Enable RAG retrieval")
    top_k: int = Field(default=5, description="Number of context chunks")
    min_score: float = Field(default=0.0, description="Minimum score threshold")
    model: str = Field(default=settings.openai_model, description="LLM model to use")


class CompletionResponse(BaseModel):
    """Response model for completion"""
    success: bool
    message: str = ""
    context: str = ""
    sources: List[dict] = []
    dialog_id: Optional[str] = None
    error: Optional[str] = None


def get_llm(model_name: str = None) -> ChatOpenAI:
    if model_name is None:
        model_name = settings.openai_model
    """
    Get LLM instance based on settings.

    Args:
        model_name: Model name to use

    Returns:
        ChatOpenAI instance
    """
    api_key = settings.openai_api_key or settings.embedding_api_key

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="No LLM API key configured. Set OPENAI_API_KEY or EMBEDDING_API_KEY"
        )

    return ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=settings.openai_base_url,
        streaming=True
    )


def create_agent_with_rag(knowledge_ids: List[str], model_name: str = None) -> ReactAgent:
    if model_name is None:
        model_name = settings.openai_model
    """
    Create a ReactAgent with RAG tool.

    Args:
        knowledge_ids: Knowledge base IDs to search
        model_name: LLM model name

    Returns:
        ReactAgent instance
    """
    # Get LLM
    chat_model = get_llm(model_name)

    # Create RAG tool
    rag_tool = create_rag_tool(knowledge_ids=knowledge_ids)

    # Create system prompt with knowledge_ids
    system_prompt = f"""你是一个智能助手，可以帮助用户回答问题。

当前可用的知识库 ID 列表: {knowledge_ids}

当用户询问需要查找知识库的问题时，你会自动使用 rag_search 工具搜索相关知识库。
IMPORTANT: 你必须使用上面的 knowledge_ids 列表中的 ID，不要自己编造或使用其他 ID。
请根据搜索到的上下文信息回答用户的问题。

如果知识库中没有相关信息，请如实告知用户。"""

    # Create agent
    agent = ReactAgent(
        model=chat_model,
        system_prompt=system_prompt,
        tools=[rag_tool]
    )

    return agent


async def generate_stream(
    agent: ReactAgent,
    message: str,
    knowledge_ids: List[str],
    session: AsyncSession,
    dialog_id: str,
    model: str,
    cache_service: HistoryCacheService,
) -> AsyncGenerator[str, None]:
    """
    Generate streaming response with SSE format and save history.

    Consistency strategy:
    1. Read history first (triggers DB backfill on cache miss while message not yet committed)
    2. In-memory merge to build full context for immediate agent response
    3. Async dual-write: concurrent DB commit + cache append via asyncio.gather
    """
    import asyncio
    from langchain_core.messages import HumanMessage, AIMessage
    from datetime import datetime

    # Collect events for history
    events = []
    accumulated_content = ""

    # Prepare user history object (not yet committed)
    user_history = ChatHistory(
        id=str(time.time() * 1000) + "_user",
        dialog_id=dialog_id,
        role="user",
        content=message,
        created_at=datetime.now()
    )
    user_history_dict = user_history.to_dict()

    # Step 1: Read history FIRST (on cache miss, backfills from DB which doesn't have this message yet)
    histories = await cache_service.get_history(dialog_id)

    # Step 2: In-memory merge - full context includes current user message
    # This ensures agent can start immediately without waiting for I/O
    full_histories = histories + [user_history_dict]

    messages = []
    for h in full_histories:
        role = h.get("role")
        content = h.get("content")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    # Step 3: Async dual-write - concurrent DB commit and cache append
    session.add(user_history)
    await asyncio.gather(
        session.commit(),
        cache_service.append_to_cache(dialog_id, user_history_dict)
    )

    start_time = time.time()

    try:
        async for event in agent.astream(messages):
            if event.get("type") == "response_chunk":
                # Text chunk: wrap in SSE format
                yield f'data: {json.dumps(event)}\n\n'
                accumulated_content += event.get("data", {}).get("chunk", "")
            else:
                # Other events (tool calls, status updates)
                yield f'data: {json.dumps(event)}\n\n'
                events.append(event)

    except Exception as e:
        from loguru import logger
        logger.error(f"Streaming error: {str(e)}")
        error_event = {
            "type": "event",
            "timestamp": time.time(),
            "data": {
                "status": "ERROR",
                "title": "Error",
                "message": f"处理请求时发生错误: {str(e)}"
            }
        }
        yield f'data: {json.dumps(error_event)}\n\n'
        events.append(error_event)

    finally:
        # Save assistant message to history (async dual-write for consistency)
        duration = time.time() - start_time
        assistant_history = ChatHistory(
            id=str(time.time() * 1000) + "_assistant",
            dialog_id=dialog_id,
            role="assistant",
            content=accumulated_content,
            events=json.dumps(events) if events else None,
            extra=json.dumps({
                "model": model,
                "duration": duration,
                "knowledge_ids": knowledge_ids
            }),
            created_at=datetime.now()
        )
        session.add(assistant_history)

        # Update dialog timestamp
        statement = select(Dialog).where(Dialog.id == dialog_id)
        result = await session.execute(statement)
        dialog = result.scalar_one_or_none()
        if dialog:
            dialog.updated_at = datetime.now()

        # Async triple-write: concurrent DB commit, cache append, and dialog update
        await asyncio.gather(
            session.commit(),
            cache_service.append_to_cache(dialog_id, assistant_history.to_dict())
        )


@router.post("/completion/stream")
async def completion_stream(
    request: CompletionRequest,
    current_user: Optional[dict] = Depends(get_optional_user),  # 改为可选认证
    db: AsyncSession = Depends(async_session_dependency),
    cache_service: HistoryCacheService = Depends(get_history_cache_service),
):
    """
    Streaming completion endpoint with RAG integration

    Flow:
    1. Receive user message + knowledge_ids
    2. Create or get dialog
    3. Create ReactAgent with RAG tool
    4. Stream tool execution events (START/END)
    5. Stream LLM response chunks
    6. Save history to database

    SSE Events:
    - type: "event" - Tool execution status
      data.status: "START" | "END" | "ERROR"
      data.title: Event title
      data.message: Event message
    - type: "response_chunk" - LLM response chunks
      data.chunk: New chunk content
      data.accumulated: Full accumulated content
    """
    import uuid

    # Validate knowledge_ids if RAG is enabled
    if request.enable_rag and not request.knowledge_ids:
        raise HTTPException(
            status_code=400,
            detail="knowledge_ids required when enable_rag is True"
        )

    try:
        # current_user 可能为 None（未登录）或 {user_id: "xxx"}（已登录）
        jwt_user_id = current_user.get("user_id") if current_user else None

        # 初始化 AgentFactory（如果是首次）
        try:
            agent_factory = get_agent_factory()
        except RuntimeError:
            # 首次初始化
            initialize_agent_factory(get_session_manager())
            agent_factory = get_agent_factory()

        # 创建 Agent（根据 user_id 自动选择工具）
        agent = agent_factory.create_agent(
            user_id=jwt_user_id,
            knowledge_ids=request.knowledge_ids,
            model_name=request.model
        )

        # Get or create dialog using DialogRepository
        # Generate dialog_id if not provided
        dialog_id = request.dialog_id or str(uuid.uuid4())
        dialog, _ = await DialogRepository.get_or_create_dialog(
            session=db,
            dialog_id=dialog_id,
            jwt_user_id=jwt_user_id,
            agent_id=request.agent_id
        )

        # Set tool context for logging
        from app.core.tools.context import set_tool_context
        set_tool_context(user_id=jwt_user_id, dialog_id=dialog.id)

        # Return streaming response
        return WatchedStreamingResponse(
            content=generate_stream(
                agent=agent,
                message=request.message,
                knowledge_ids=request.knowledge_ids,
                session=db,
                dialog_id=dialog.id,
                model=request.model,
                cache_service=cache_service,
            ),
            media_type="text/event-stream",
            headers={"X-Dialog-ID": dialog.id}
        )

    except HTTPException:
        raise
    except Exception as e:
        from loguru import logger
        logger.error(f"Completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/completion", response_model=CompletionResponse)
async def completion(
    request: CompletionRequest,
    current_user: Optional[dict] = Depends(get_optional_user),
    db: AsyncSession = Depends(async_session_dependency),
):
    """
    Completion endpoint with RAG integration (non-streaming)

    Flow:
    1. Receive user message
    2. Create or get dialog
    3. Retrieve context from RAG
    4. Save history to database
    5. Return message + context + sources
    """
    import uuid
    from datetime import datetime

    try:
        # Get jwt_user_id from current_user
        jwt_user_id = current_user.get("user_id") if current_user else None

        # Get or create dialog using DialogRepository
        # Generate dialog_id if not provided
        dialog_id = request.dialog_id or str(uuid.uuid4())
        dialog, _ = await DialogRepository.get_or_create_dialog(
            session=db,
            dialog_id=dialog_id,
            jwt_user_id=jwt_user_id,
            agent_id=request.agent_id
        )

        context = ""
        sources = []

        # Save user message
        user_history = ChatHistory(
            id=str(time.time() * 1000) + "_user",
            dialog_id=dialog.id,
            role="user",
            content=request.message,
            created_at=datetime.now()
        )
        db.add(user_history)

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

        # Save assistant message
        assistant_history = ChatHistory(
            id=str(time.time() * 1000) + "_assistant",
            dialog_id=dialog.id,
            role="assistant",
            content=context,
            extra=json.dumps({
                "model": request.model,
                "knowledge_ids": request.knowledge_ids,
                "sources": sources
            }),
            created_at=datetime.now()
        )
        db.add(assistant_history)
        await db.commit()

        return CompletionResponse(
            success=True,
            message=request.message,
            context=context,
            sources=sources,
            dialog_id=dialog.id
        )

    except Exception as e:
        return CompletionResponse(
            success=False,
            message=request.message,
            error=str(e)
        )
