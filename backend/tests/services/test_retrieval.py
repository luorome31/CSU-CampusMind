"""
Hybrid Retrieval 服务测试
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.schema.search import SearchModel


class TestHybridRetrieval:
    """HybridRetrieval 业务逻辑测试"""

    @pytest.fixture
    def mock_vector_db(self):
        """Mock vector_db"""
        with patch("app.services.rag.retrieval.vector_db") as mock:
            mock.search = AsyncMock(return_value=[
                SearchModel(
                    content="Vector result",
                    chunk_id="vec_1",
                    file_id="file_1",
                    file_name="vec.txt",
                    knowledge_id="kb_1",
                    score=0.9
                )
            ])
            yield mock

    @pytest.fixture
    def mock_es_client(self):
        """Mock es_client"""
        with patch("app.services.rag.retrieval.es_client") as mock:
            mock.search = MagicMock(return_value=[
                {
                    "content": "ES result",
                    "chunk_id": "es_1",
                    "file_id": "file_2",
                    "file_name": "es.txt",
                    "knowledge_id": "kb_1",
                    "score": 0.85
                }
            ])
            yield mock

    @pytest.mark.asyncio
    async def test_mix_retrieve_both_enabled(self, mock_vector_db, mock_es_client):
        """测试混合检索-向量和关键词都启用"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.mix_retrieve(
            query="test query",
            knowledge_ids=["kb_1"],
            enable_vector=True,
            enable_keyword=True,
            top_k=5
        )

        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_mix_retrieve_vector_only(self, mock_vector_db, mock_es_client):
        """测试混合检索-仅向量"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.mix_retrieve(
            query="test query",
            knowledge_ids=["kb_1"],
            enable_vector=True,
            enable_keyword=False,
            top_k=5
        )

        # Should only call vector search
        mock_vector_db.search.assert_called()

    @pytest.mark.asyncio
    async def test_mix_retrieve_keyword_only(self, mock_vector_db, mock_es_client):
        """测试混合检索-仅关键词"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.mix_retrieve(
            query="test query",
            knowledge_ids=["kb_1"],
            enable_vector=False,
            enable_keyword=True,
            top_k=5
        )

        # Should only call ES search
        mock_es_client.search.assert_called()

    @pytest.mark.asyncio
    async def test_mix_retrieve_both_disabled(self, mock_vector_db, mock_es_client):
        """测试混合检索-都禁用"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.mix_retrieve(
            query="test query",
            knowledge_ids=["kb_1"],
            enable_vector=False,
            enable_keyword=False,
            top_k=5
        )

        assert results == []
        mock_vector_db.search.assert_not_called()
        mock_es_client.search.assert_not_called()

    @pytest.mark.asyncio
    async def test_retrieve_vector_documents(self, mock_vector_db):
        """测试向量检索"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.retrieve_vector_documents(
            query="test",
            knowledge_ids=["kb_1", "kb_2"],
            top_k=5
        )

        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_retrieve_keyword_documents(self, mock_es_client):
        """测试关键词检索"""
        from app.services.rag.retrieval import HybridRetrieval

        results = await HybridRetrieval.retrieve_keyword_documents(
            query="test",
            knowledge_ids=["kb_1", "kb_2"],
            top_k=5
        )

        assert len(results) >= 1


class TestHybridRetrievalDeduplication:
    """测试去重逻辑"""

    @pytest.mark.asyncio
    async def test_deduplicate_by_chunk_id(self):
        """测试按 chunk_id 去重"""
        with patch("app.services.rag.retrieval.vector_db") as mock_vec, \
             patch("app.services.rag.retrieval.es_client") as mock_es:

            # Both return same chunk_id
            mock_vec.search = AsyncMock(return_value=[
                SearchModel(
                    content="Content 1",
                    chunk_id="same_id",
                    file_id="file_1",
                    file_name="test.txt",
                    knowledge_id="kb_1",
                    score=0.9
                )
            ])
            mock_es.search = MagicMock(return_value=[
                {
                    "content": "Content 2",
                    "chunk_id": "same_id",  # Same chunk_id
                    "file_id": "file_1",
                    "file_name": "test.txt",
                    "knowledge_id": "kb_1",
                    "score": 0.8
                }
            ])

            from app.services.rag.retrieval import HybridRetrieval

            results = await HybridRetrieval.mix_retrieve(
                query="test",
                knowledge_ids=["kb_1"],
                enable_vector=True,
                enable_keyword=True,
                top_k=5
            )

            # Should only have one result (deduplicated)
            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_top_k_limit(self):
        """测试 top_k 限制"""
        with patch("app.services.rag.retrieval.vector_db") as mock_vec, \
             patch("app.services.rag.retrieval.es_client") as mock_es:

            # Return many results
            mock_vec.search = AsyncMock(return_value=[
                SearchModel(
                    content=f"Content {i}",
                    chunk_id=f"vec_{i}",
                    file_id=f"file_{i}",
                    file_name=f"test{i}.txt",
                    knowledge_id="kb_1",
                    score=0.9 - i * 0.1
                )
                for i in range(10)
            ])
            mock_es.search = MagicMock(return_value=[
                {
                    "content": f"ES Content {i}",
                    "chunk_id": f"es_{i}",
                    "file_id": f"file_{i}",
                    "file_name": f"es{i}.txt",
                    "knowledge_id": "kb_1",
                    "score": 0.8 - i * 0.1
                }
                for i in range(10)
            ])

            from app.services.rag.retrieval import HybridRetrieval

            results = await HybridRetrieval.mix_retrieve(
                query="test",
                knowledge_ids=["kb_1"],
                enable_vector=True,
                enable_keyword=True,
                top_k=3  # Limit to 3
            )

            # Should only return top_k results
            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_sort_by_score_descending(self):
        """测试按分数降序排序"""
        with patch("app.services.rag.retrieval.vector_db") as mock_vec, \
             patch("app.services.rag.retrieval.es_client") as mock_es:

            # Return unsorted results
            mock_vec.search = AsyncMock(return_value=[
                SearchModel(
                    content="Low score",
                    chunk_id="low",
                    file_id="file_1",
                    file_name="low.txt",
                    knowledge_id="kb_1",
                    score=0.3
                )
            ])
            mock_es.search = MagicMock(return_value=[
                {
                    "content": "High score",
                    "chunk_id": "high",
                    "file_id": "file_2",
                    "file_name": "high.txt",
                    "knowledge_id": "kb_1",
                    "score": 0.9
                }
            ])

            from app.services.rag.retrieval import HybridRetrieval

            results = await HybridRetrieval.mix_retrieve(
                query="test",
                knowledge_ids=["kb_1"],
                enable_vector=True,
                enable_keyword=True,
                top_k=5
            )

            # First result should have highest score
            assert results[0].score >= results[1].score
