"""
RAG Indexer - Orchestrates indexing pipeline
"""
import uuid
from typing import List, Optional
from loguru import logger

from app.schema.chunk import ChunkModel
from app.services.rag.chunker import default_chunker
from app.services.rag.embedding import embedding_service
from app.services.rag.vector_db import vector_db
from app.services.rag.es_client import es_client


class Indexer:
    """RAG Indexer - handles content indexing to vector and keyword DBs"""

    def __init__(
        self,
        chunk_size: int = 500,
        overlap_size: int = 100,
        enable_vector: bool = True,
        enable_keyword: bool = True
    ):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.enable_vector = enable_vector
        self.enable_keyword = enable_keyword

    async def index_content(
        self,
        content: str,
        knowledge_id: str,
        source_name: str = "crawl",
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Index content to vector DB and/or keyword DB

        Args:
            content: Text content to index
            knowledge_id: Knowledge base ID (used as collection/index name)
            source_name: Source file name
            metadata: Additional metadata

        Returns:
            dict with success status and indexed chunk count
        """
        try:
            # Generate file_id
            file_id = metadata.get("file_id") if metadata else str(uuid.uuid4())
            if not file_id:
                file_id = str(uuid.uuid4())

            # Chunk the content
            chunker = TextChunker(self.chunk_size, self.overlap_size)
            chunks = chunker.chunk_text(
                text=content,
                file_id=file_id,
                file_name=source_name,
                knowledge_id=knowledge_id
            )

            if not chunks:
                return {
                    "success": False,
                    "error": "No chunks generated",
                    "chunk_count": 0
                }

            indexed_count = 0

            # Store to vector DB (ChromaDB)
            if self.enable_vector:
                # Get embeddings
                texts = [chunk.content for chunk in chunks]
                embeddings = await embedding_service.get_embeddings(texts)

                # Insert to ChromaDB
                success = await vector_db.insert_chunks(
                    collection_name=knowledge_id,
                    chunks=chunks,
                    embeddings=embeddings
                )
                if success:
                    indexed_count += len(chunks)
                    logger.info(f"Indexed {len(chunks)} chunks to ChromaDB")
                else:
                    logger.error("Failed to index to ChromaDB")

            # Store to keyword DB (Elasticsearch)
            if self.enable_keyword:
                success = es_client.insert_chunks(
                    index_name=knowledge_id,
                    chunks=chunks
                )
                if success:
                    logger.info(f"Indexed {len(chunks)} chunks to Elasticsearch")
                else:
                    logger.error("Failed to index to Elasticsearch")

            return {
                "success": True,
                "chunk_count": len(chunks),
                "file_id": file_id,
                "knowledge_id": knowledge_id
            }

        except Exception as e:
            logger.error(f"Indexing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "chunk_count": 0
            }

    async def index_from_oss(
        self,
        oss_url: str,
        knowledge_id: str,
        storage_client
    ) -> dict:
        """
        Index content from OSS

        Args:
            oss_url: OSS URL of the content file
            knowledge_id: Knowledge base ID
            storage_client: Storage client to download file

        Returns:
            dict with success status
        """
        try:
            # Download content from OSS
            # For now, assume it's markdown/text content
            # Extract object key from URL
            from urllib.parse import urlparse
            parsed = urlparse(oss_url)
            object_key = parsed.path.lstrip('/')

            # Download to temp location
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(delete=False, suffix='.md') as tmp:
                tmp_path = tmp.name

            try:
                storage_client.download_file(object_key, tmp_path)

                # Read content
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract filename from object key
                file_name = os.path.basename(object_key)

                # Index content
                return await self.index_content(
                    content=content,
                    knowledge_id=knowledge_id,
                    source_name=file_name,
                    metadata={"file_id": str(uuid.uuid4())}
                )
            finally:
                # Cleanup temp file
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            logger.error(f"Indexing from OSS failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Need to import TextChunker for indexer
from app.services.rag.chunker import TextChunker

# Default indexer
indexer = Indexer()
