"""
RAG Tool - Wrapper for RagHandler as LangChain BaseTool
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from loguru import logger

from app.services.rag.handler import rag_handler


# Tool input schema
class RagToolInput(BaseModel):
    """Input schema for RAG tool"""
    query: str = Field(..., description="The search query/question to find relevant context")
    knowledge_ids: List[str] = Field(
        ...,
        description="List of knowledge base IDs to search in"
    )
    top_k: int = Field(
        default=5,
        description="Number of top results to return"
    )
    min_score: float = Field(
        default=0.0,
        description="Minimum score threshold for filtering results"
    )


class RagToolResult(BaseModel):
    """Result from RAG tool execution"""
    context: str = Field(..., description="Retrieved context content")
    sources: List[dict] = Field(default=[], description="Source information")


# --- RAG Tool ---

class RagTool(BaseTool):
    """
    A LangChain tool that provides RAG (Retrieval-Augmented Generation) capabilities.

    This tool searches through knowledge bases and retrieves relevant context
    to help answer user questions.
    """

    name: str = "rag_search"
    description: str = """
    Search knowledge bases to retrieve relevant context for answering user questions.

    CRITICAL: You MUST use the exact knowledge_ids provided in the conversation context.
    DO NOT use arbitrary IDs like 'python', 'default', or any ID not in the provided list.

    Input should be a JSON object with:
    - query: The question to search for
    - knowledge_ids: List of knowledge base IDs to search (MUST use provided IDs)
    - top_k: Number of results to return (default: 5)
    - min_score: Minimum relevance score (default: 0.0)
    """
    args_schema: type[BaseModel] = RagToolInput

    async def _arun(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5,
        min_score: float = 0.0
    ) -> str:
        """
        Async execution of RAG search.

        Returns:
            Formatted string with context and sources
        """
        logger.info(f"RAG tool called with query: {query[:50]}..., knowledge_ids: {knowledge_ids}")

        try:
            result = await rag_handler.retrieve_with_sources(
                query=query,
                knowledge_ids=knowledge_ids,
                top_k=top_k,
                min_score=min_score
            )

            context = result.get("context", "")
            sources = result.get("sources", [])

            if not context:
                return "未找到相关信息。"

            # Format response
            response_parts = [
                "=== 相关上下文 ===",
                context,
                "=== 来源 ==="
            ]

            if sources:
                for i, source in enumerate(sources, 1):
                    response_parts.append(
                        f"{i}. {source.get('file_name', 'Unknown')} (相关度: {source.get('score', 0):.2f})"
                    )
            else:
                response_parts.append("无来源信息")

            return "\n\n".join(response_parts)

        except Exception as e:
            logger.error(f"RAG tool error: {str(e)}")
            return f"搜索知识库时发生错误: {str(e)}"

    def _run(
        self,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5,
        min_score: float = 0.0
    ) -> str:
        """
        Sync execution of RAG search (fallback).
        """
        # For sync execution, we need to run the async version
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, create new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(
                        asyncio.run,
                        self._arun(query, knowledge_ids, top_k, min_score)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(
                    self._arun(query, knowledge_ids, top_k, min_score)
                )
        except RuntimeError:
            return asyncio.run(
                self._arun(query, knowledge_ids, top_k, min_score)
            )


def create_rag_tool(knowledge_ids: List[str] = None) -> RagTool:
    """
    Factory function to create a RAG tool instance.

    Args:
        knowledge_ids: Default knowledge base IDs to search (optional)

    Returns:
        RagTool instance
    """
    return RagTool()
