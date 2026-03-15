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
        """Get ES index configuration - matching reference project"""
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "ik_analyzer": {
                            "type": "custom",
                            "tokenizer": "ik_smart"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "content": {"type": "text", "analyzer": "ik_analyzer"},
                    "summary": {"type": "text", "analyzer": "ik_analyzer"},
                    "file_id": {"type": "keyword"},
                    "file_name": {"type": "keyword"},
                    "knowledge_id": {"type": "keyword"},
                    "update_time": {"type": "date", "format": "strict_date_optional_time||epoch_millis"}
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
        """Search chunks by keyword - matching reference project ES search logic"""
        if not self.client:
            logger.warning("ES client not initialized")
            return []

        try:
            # Check if index exists first
            if not self.client.indices.exists(index=index_name):
                logger.warning(f"ES index '{index_name}' does not exist")
                return []

            # Build search query matching reference project
            # - operator: and (all terms must match)
            # - minimum_should_match: 75%
            # - fuzziness: AUTO
            # - boost: 2.0
            search_body = {
                "size": top_k,
                "timeout": "3s",
                "query": {
                    "match": {
                        "content": {
                            "query": query,
                            "analyzer": "ik_analyzer",
                            "operator": "and",
                            "minimum_should_match": "75%",
                            "fuzziness": "AUTO",
                            "boost": 2.0
                        }
                    }
                }
            }

            logger.debug(f"ES search query: '{query}' on index: {index_name}")

            response = self.client.search(
                index=index_name,
                body=search_body
            )

            # Debug: log response
            logger.debug(f"ES response: {response}")

            results = []
            total_hits = response['hits']['total']['value'] if isinstance(response['hits']['total'], dict) else response['hits']['total']
            logger.info(f"ES total hits: {total_hits}")

            # Check if there's a valid max_score (not 0 or None)
            if not response['hits'].get('max_score'):
                logger.info("ES max_score is 0 or None, no relevant results")
                return []

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

            logger.info(f"ES returning {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def search_summary(
        self,
        index_name: str,
        query: str,
        top_k: int = 5
    ) -> List[dict]:
        """Search by summary field - matching reference project"""
        if not self.client:
            logger.warning("ES client not initialized")
            return []

        try:
            if not self.client.indices.exists(index=index_name):
                logger.warning(f"ES index '{index_name}' does not exist")
                return []

            search_body = {
                "size": top_k,
                "timeout": "3s",
                "query": {
                    "match": {
                        "summary": {
                            "query": query,
                            "analyzer": "ik_analyzer",
                            "operator": "and",
                            "minimum_should_match": "75%",
                            "fuzziness": "AUTO",
                            "boost": 2.0
                        }
                    }
                }
            }

            logger.debug(f"ES search summary query: '{query}' on index: {index_name}")

            response = self.client.search(
                index=index_name,
                body=search_body
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

            logger.info(f"ES summary search returning {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Summary search failed: {e}")
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


# Default instance - configured from settings
from app.config import settings

_es_client = None


def get_es_client() -> ESClient:
    """Get or create Elasticsearch client with settings from config"""
    global _es_client
    if _es_client is None:
        _es_client = ESClient(hosts=settings.elasticsearch_hosts)
    return _es_client


es_client = get_es_client()
