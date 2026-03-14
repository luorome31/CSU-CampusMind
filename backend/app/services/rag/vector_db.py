"""
Vector Database Client - ChromaDB implementation with search
"""
from typing import List, Optional, Dict
import chromadb
from loguru import logger

from app.schema.chunk import ChunkModel
from app.schema.search import SearchModel
from app.services.rag.embedding import embedding_service


class ChromaClient:
    """ChromaDB client for vector storage and retrieval"""

    def __init__(self, persist_path: str = "./data/chroma"):
        self.collections: Dict[str, chromadb.Collection] = {}
        self.client = None
        self.persist_path = persist_path
        self._connect()

    def _connect(self):
        """Establish Chroma connection"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_path)
            logger.info(f"Connected to Chroma at {self.persist_path}")
        except Exception as e:
            logger.error(f"Failed to connect to Chroma: {e}")
            raise

    def _get_collection(self, collection_name: str) -> Optional[chromadb.Collection]:
        """Get collection by name"""
        try:
            if collection_name not in self.collections:
                collection = self.client.get_collection(collection_name)
                self.collections[collection_name] = collection
            return self.collections.get(collection_name)
        except Exception:
            return None

    def create_collection(self, collection_name: str) -> bool:
        """Create a new collection"""
        try:
            if self._collection_exists(collection_name):
                logger.info(f"Collection '{collection_name}' already exists")
                return True

            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.collections[collection_name] = collection
            logger.info(f"Created collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def _collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists"""
        try:
            self.client.get_collection(collection_name)
            return True
        except Exception:
            return False

    async def insert_chunks(
        self,
        collection_name: str,
        chunks: List[ChunkModel],
        embeddings: List[List[float]]
    ) -> bool:
        """Insert chunks into collection"""
        if not chunks or not embeddings:
            logger.warning("No chunks or embeddings to insert")
            return True

        # Ensure collection exists
        if not self._collection_exists(collection_name):
            self.create_collection(collection_name)

        collection = self._get_collection(collection_name)
        if not collection:
            logger.error(f"Cannot insert - collection '{collection_name}' unavailable")
            return False

        try:
            ids = [chunk.chunk_id for chunk in chunks]
            documents = [chunk.content for chunk in chunks]
            metadatas = [
                {
                    "chunk_id": chunk.chunk_id,
                    "file_id": chunk.file_id,
                    "file_name": chunk.file_name,
                    "knowledge_id": chunk.knowledge_id,
                    "update_time": chunk.update_time,
                    "summary": chunk.summary or "",
                }
                for chunk in chunks
            ]

            # Batch insert
            batch_size = 100
            for i in range(0, len(ids), batch_size):
                batch_ids = ids[i:i + batch_size]
                batch_docs = documents[i:i + batch_size]
                batch_emb = embeddings[i:i + batch_size]
                batch_meta = metadatas[i:i + batch_size]

                collection.add(
                    ids=batch_ids,
                    documents=batch_docs,
                    embeddings=batch_emb,
                    metadatas=batch_meta
                )

            logger.info(f"Inserted {len(chunks)} chunks into '{collection_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to insert chunks: {e}")
            return False

    async def search(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[SearchModel]:
        """Search similar chunks by query text"""
        collection = self._get_collection(collection_name)
        if not collection:
            logger.error(f"Collection '{collection_name}' not found")
            return []

        try:
            # Get query embedding
            query_embedding = await embedding_service.get_embedding(query)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k * 2, 100),  # Get more for reranking
                include=["metadatas", "documents", "distances"]
            )

            if not results['ids'] or len(results['ids'][0]) == 0:
                return []

            search_results = []
            for i in range(len(results['ids'][0])):
                metadata = results['metadatas'][0][i] or {}
                search_results.append(SearchModel(
                    content=results['documents'][0][i] or "",
                    chunk_id=metadata.get("chunk_id", ""),
                    file_id=metadata.get("file_id", ""),
                    file_name=metadata.get("file_name", ""),
                    knowledge_id=metadata.get("knowledge_id", ""),
                    update_time=metadata.get("update_time", ""),
                    summary=metadata.get("summary", ""),
                    score=1.0 - results['distances'][0][i]  # Convert distance to similarity
                ))

            return search_results[:top_k]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def search_summary(
        self,
        collection_name: str,
        query: str,
        top_k: int = 5
    ) -> List[SearchModel]:
        """Search similar chunks by summary"""
        # Similar to search but could filter by is_summary=True
        return await self.search(collection_name, query, top_k)

    async def delete_by_file_id(self, file_id: str, collection_name: str) -> bool:
        """Delete chunks by file_id"""
        collection = self._get_collection(collection_name)
        if not collection:
            return False

        try:
            collection.delete(where={"file_id": file_id})
            logger.info(f"Deleted chunks for file_id: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False


# Default instance
vector_db = ChromaClient()
