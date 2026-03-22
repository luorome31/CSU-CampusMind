"""
RAG Handler 服务测试
"""
import pytest
from unittest.mock import patch, AsyncMock
from app.schema.search import SearchModel


class TestRagHandler:
    """RagHandler 业务逻辑测试"""

    @pytest.fixture
    def mock_hybrid_retrieval(self):
        """Mock hybrid_retrieval"""
        with patch("app.services.rag.handler.hybrid_retrieval") as mock:
            # Create mock search results
            mock_docs = [
                SearchModel(
                    content="Python is a programming language.",
                    chunk_id="chunk_1",
                    file_id="file_1",
                    file_name="python.txt",
                    knowledge_id="kb_1",
                    score=0.95
                ),
                SearchModel(
                    content="FastAPI is a web framework.",
                    chunk_id="chunk_2",
                    file_id="file_2",
                    file_name="fastapi.txt",
                    knowledge_id="kb_1",
                    score=0.85
                )
            ]
            mock.mix_retrieve = AsyncMock(return_value=mock_docs)
            yield mock

    @pytest.mark.asyncio
    async def test_retrieve_with_sources_success(self, mock_hybrid_retrieval):
        """测试带来源的检索成功"""
        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve_with_sources(
            query="What is Python?",
            knowledge_ids=["kb_1"],
            top_k=5,
            min_score=0.0
        )

        assert result["context"] == "Python is a programming language.\n\nFastAPI is a web framework."
        assert len(result["sources"]) == 2

    @pytest.mark.asyncio
    async def test_retrieve_with_sources_empty_knowledge_ids(self):
        """测试空 knowledge_ids"""
        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve_with_sources(
            query="test",
            knowledge_ids=[],
            top_k=5
        )

        assert result["context"] == ""
        assert result["sources"] == []

    @pytest.mark.asyncio
    async def test_retrieve_with_sources_min_score_filter(self, mock_hybrid_retrieval):
        """测试 min_score 过滤"""
        result = await import_module("app.services.rag.handler").RagHandler.retrieve_with_sources(
            query="test",
            knowledge_ids=["kb_1"],
            min_score=0.9  # Only keep score >= 0.9
        )

        # Only one document has score >= 0.9
        assert "Python is a programming language" in result["context"]

    @pytest.mark.asyncio
    async def test_retrieve_with_sources_no_results(self, mock_hybrid_retrieval):
        """测试无结果"""
        mock_hybrid_retrieval.mix_retrieve = AsyncMock(return_value=[])

        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve_with_sources(
            query="test",
            knowledge_ids=["kb_1"]
        )

        assert result["context"] == "No relevant documents found."
        assert result["sources"] == []

    @pytest.mark.asyncio
    async def test_retrieve_success(self, mock_hybrid_retrieval):
        """测试基础检索方法"""
        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve(
            query="What is Python?",
            knowledge_ids=["kb_1"]
        )

        assert "Python is a programming language" in result

    @pytest.mark.asyncio
    async def test_retrieve_empty_knowledge_ids(self):
        """测试基础检索空 knowledge_ids"""
        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve(
            query="test",
            knowledge_ids=[]
        )

        assert result == ""

    @pytest.mark.asyncio
    async def test_deduplicate_sources(self, mock_hybrid_retrieval):
        """测试来源去重"""
        # Return duplicate documents with same file_name but different content
        mock_hybrid_retrieval.mix_retrieve = AsyncMock(return_value=[
            SearchModel(
                content="Content 1",
                chunk_id="chunk_1",
                file_id="file_1",
                file_name="test.txt",
                knowledge_id="kb_1",
                score=0.9
            ),
            SearchModel(
                content="Content 2",
                chunk_id="chunk_2",
                file_id="file_1",  # Same file_id
                file_name="test.txt",  # Same file_name
                knowledge_id="kb_1",
                score=0.8
            )
        ])

        from app.services.rag.handler import RagHandler

        result = await RagHandler.retrieve_with_sources(
            query="test",
            knowledge_ids=["kb_1"]
        )

        # Should have only one source (deduplicated)
        assert len(result["sources"]) == 1


class TestRagHandlerEdgeCases:
    """RagHandler 边界情况测试"""

    @pytest.mark.asyncio
    async def test_retrieve_low_min_score(self):
        """测试低 min_score"""
        with patch("app.services.rag.handler.hybrid_retrieval") as mock:
            mock.mix_retrieve = AsyncMock(return_value=[
                SearchModel(
                    content="Test",
                    chunk_id="chunk_1",
                    file_id="file_1",
                    file_name="test.txt",
                    knowledge_id="kb_1",
                    score=0.1  # Low score
                )
            ])

            from app.services.rag.handler import RagHandler

            result = await RagHandler.retrieve_with_sources(
                query="test",
                knowledge_ids=["kb_1"],
                min_score=0.0  # Accept all
            )

            assert result["sources"][0]["score"] == 0.1


# Helper function
def import_module(name):
    import importlib
    return importlib.import_module(name)
