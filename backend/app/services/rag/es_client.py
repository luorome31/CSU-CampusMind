"""
Elasticsearch Client - Keyword search
"""
from typing import List, Optional
from elasticsearch import Elasticsearch
from loguru import logger

from app.schema.chunk import ChunkModel


class ESClient:
    """Elasticsearch client for keyword search"""

    def __init__(self, hosts: str = "http://localhost:9200"):
        self.hosts = hosts
        self.client = None
        self._connect()

    def _connect(self):
        """Establish ES connection"""
        try:
            self.client = Elasticsearch([self.hosts])
            logger.info(f"Connected to Elasticsearch at {self.hosts}")
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            # Continue anyway - may be used later

    def _get_index_config(self) -> dict:
        """Get ES index configuration"""
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "ik_max_word": {
                            "type": "standard"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "file_id": {"type": "keyword"},
                    "file_name": {"type": "keyword"},
                    "knowledge_id": {"type": "keyword"},
                    "update_time": {"type": "date"},
                    "summary": {"type": "text", "analyzer": "standard"}
                }
            }
        }

    def create_index(self, index_name: str) -> bool:
        """Create index if not exists"""
        if not self.client:
            logger.warning("ES client not initialized")
            return False

        try:
            if self.client.indices.exists(index=index_name):
                logger.info(f"Index '{index_name}' already exists")
                return True

            self.client.indices.create(index=index_name, body=self._get_index_config())
            logger.info(f"Created index: {index_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create index: {e}")
            return False

    def insert_chunks(self, index_name: str, chunks: List[ChunkModel]) -> bool:
        """Insert chunks into index"""
        if not self.client:
            logger.warning("ES client not initialized")
            return False

        if not chunks:
            return True

        # Ensure index exists
        self.create_index(index_name)

        try:
            for chunk in chunks:
                self.client.index(
                    index=index_name,
                    id=chunk.chunk_id,
                    body=chunk.to_dict()
                )
            logger.info(f"Inserted {len(chunks)} chunks into '{index_name}'")
            return True
        except Exception as e:
            logger.error(f"Failed to insert chunks: {e}")
            return False

    def search(
        self,
        index_name: str,
        query: str,
        top_k: int = 5
    ) -> List[dict]:
        """Search chunks by keyword"""
        if not self.client:
            logger.warning("ES client not initialized")
            return []

        try:
            response = self.client.search(
                index=index_name,
                body={
                    "query": {
                        "match": {
                            "content": query
                        }
                    },
                    "size": top_k
                }
            )

            results = []
            for hit in response['hits']['hits']:
                source = hit['_source']
                results.append({
                    "content": source.get("content", ""),
                    "chunk_id": source.get("chunk_id", ""),
                    "file_id": source.get("file_id", ""),
                    "file_name": source.get("file_name", ""),
                    "knowledge_id": source.get("knowledge_id", ""),
                    "score": hit['_score']
                })

            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_by_file_id(self, index_name: str, file_id: str) -> bool:
        """Delete chunks by file_id"""
        if not self.client:
            return False

        try:
            self.client.delete_by_query(
                index=index_name,
                body={"query": {"term": {"file_id": file_id}}}
            )
            logger.info(f"Deleted chunks for file_id: {file_id}")
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False


# Default instance
es_client = ESClient()
