"""
RAG Handler - Main orchestration for retrieval
"""
from typing import List
from loguru import logger

from app.services.rag.retrieval import hybrid_retrieval


class RagHandler:
    """RAG Handler for query processing and retrieval"""

    @classmethod
    async def retrieve(
        cls,
        query: str,
        knowledge_ids: List[str],
        enable_vector: bool = True,
        enable_keyword: bool = True,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> str:
        """
        Main RAG retrieval method

        Args:
            query: User query
            knowledge_ids: List of knowledge base IDs to search
            enable_vector: Enable vector search
            enable_keyword: Enable keyword search
            top_k: Number of results to return
            min_score: Minimum score threshold

        Returns:
            Concatenated context string for LLM
        """
        if not knowledge_ids:
            logger.warning("No knowledge_ids provided for retrieval")
            return ""

        # Perform hybrid retrieval
        results = await hybrid_retrieval.mix_retrieve(
            query=query,
            knowledge_ids=knowledge_ids,
            enable_vector=enable_vector,
            enable_keyword=enable_keyword,
            top_k=top_k
        )

        # Filter by min_score
        filtered = [doc for doc in results if doc.score >= min_score]

        if not filtered:
            logger.info(f"No documents found above min_score {min_score}")
            return "No relevant documents found."

        # Concatenate content
        context = "\n\n".join(doc.content for doc in filtered)
        logger.info(f"Retrieved {len(filtered)} documents for query: {query[:50]}...")

        return context

    @classmethod
    async def retrieve_with_sources(
        cls,
        query: str,
        knowledge_ids: List[str],
        enable_vector: bool = True,
        enable_keyword: bool = True,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> dict:
        """
        RAG retrieval with source information

        Returns:
            dict with 'context' and 'sources' keys
        """
        if not knowledge_ids:
            return {"context": "", "sources": []}

        results = await hybrid_retrieval.mix_retrieve(
            query=query,
            knowledge_ids=knowledge_ids,
            enable_vector=enable_vector,
            enable_keyword=enable_keyword,
            top_k=top_k
        )

        filtered = [doc for doc in results if doc.score >= min_score]

        if not filtered:
            return {"context": "No relevant documents found.", "sources": []}

        # Extract sources
        sources = []
        seen = set()
        for doc in filtered:
            if doc.file_name not in seen:
                seen.add(doc.file_name)
                sources.append({
                    "file_name": doc.file_name,
                    "chunk_id": doc.chunk_id,
                    "score": doc.score
                })

        context = "\n\n".join(doc.content for doc in filtered)

        return {
            "context": context,
            "sources": sources
        }


# Default instance
rag_handler = RagHandler()
