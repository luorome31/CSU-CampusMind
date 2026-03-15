"""
Hybrid Retrieval - Combine ES and ChromaDB results
"""
from typing import List
from loguru import logger

from app.services.rag.vector_db import vector_db
from app.services.rag.es_client import es_client
from app.schema.search import SearchModel


class HybridRetrieval:
    """Hybrid retrieval combining ES and ChromaDB"""

    @classmethod
    async def retrieve_vector_documents(
        cls,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5
    ) -> List[SearchModel]:
        """Retrieve from ChromaDB (vector similarity)"""
        documents = []
        for knowledge_id in knowledge_ids:
            docs = await vector_db.search(knowledge_id, query, top_k)
            documents.extend(docs)
        return documents

    @classmethod
    async def retrieve_keyword_documents(
        cls,
        query: str,
        knowledge_ids: List[str],
        top_k: int = 5
    ) -> List[SearchModel]:
        """Retrieve from Elasticsearch (keyword/BM25)"""
        documents = []
        for knowledge_id in knowledge_ids:
            docs = es_client.search(knowledge_id, query, top_k)
            # Convert dict to SearchModel
            for doc in docs:
                documents.append(SearchModel(**doc))
        return documents

    @classmethod
    async def mix_retrieve(
        cls,
        query: str,
        knowledge_ids: List[str],
        enable_vector: bool = True,
        enable_keyword: bool = True,
        top_k: int = 5
    ) -> List[SearchModel]:
        """
        Hybrid retrieval: combine vector and keyword search

        Args:
            query: User query
            knowledge_ids: List of knowledge base IDs
            enable_vector: Enable vector search
            enable_keyword: Enable keyword search
            top_k: Number of results per source

        Returns:
            Merged and deduplicated results
        """
        all_documents = []

        # Vector search (ChromaDB)
        if enable_vector:
            vector_docs = await cls.retrieve_vector_documents(query, knowledge_ids, top_k)
            all_documents.extend(vector_docs)
            logger.info(f"Vector retrieval: {len(vector_docs)} docs")

        # Keyword search (Elasticsearch)
        if enable_keyword:
            keyword_docs = await cls.retrieve_keyword_documents(query, knowledge_ids, top_k)
            all_documents.extend(keyword_docs)
            logger.info(f"Keyword retrieval: {len(keyword_docs)} docs")

        # Deduplicate by chunk_id, keep highest score
        seen_chunk_ids = set()
        deduplicated = []

        # Sort by score descending
        all_documents.sort(key=lambda x: x.score, reverse=True)

        for doc in all_documents:
            if doc.chunk_id not in seen_chunk_ids:
                seen_chunk_ids.add(doc.chunk_id)
                deduplicated.append(doc)

        # Return top_k results
        return deduplicated[:top_k]


# Default instance
hybrid_retrieval = HybridRetrieval()
