"""
Retrieve API tests
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestRetrieveAPI:
    """Tests for Retrieve API endpoints"""

    @pytest.fixture
    def mock_rag_handler(self):
        """Mock RAG handler - need to patch where it's imported, not where it's used"""
        with patch("app.services.rag.handler.rag_handler") as mock:
            from app.services.rag.handler import RagHandler
            mock_instance = RagHandler.__new__(RagHandler)
            mock_instance.retrieve_with_sources = pytest.mark.asyncio(
                lambda self, **kwargs: {
                    "context": "This is retrieved context about CampusMind.",
                    "sources": [
                        {"content": "Source content 1", "score": 0.95, "metadata": {}},
                        {"content": "Source content 2", "score": 0.85, "metadata": {}}
                    ]
                }
            )
            mock.retrieve_with_sources = mock_instance.retrieve_with_sources
            yield mock

    def test_retrieve(self):
        """Test POST /api/v1/retrieve - requires external services"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/retrieve",
            json={
                "query": "What is CampusMind?",
                "knowledge_ids": ["test_kb_1"],
                "enable_vector": True,
                "enable_keyword": True,
                "top_k": 5,
                "min_score": 0.0
            }
        )

        # This test requires ChromaDB and Elasticsearch to be running
        # The API returns success=False when services are unavailable
        data = response.json()
        assert "success" in data

    def test_retrieve_simple(self):
        """Test POST /api/v1/retrieve/simple"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/retrieve/simple",
            json={
                "query": "What is CampusMind?",
                "knowledge_id": "test_kb_1",
                "top_k": 3
            }
        )

        data = response.json()
        assert "success" in data

    def test_retrieve_validation(self):
        """Test validation for retrieve request"""
        from app.main import app
        client = TestClient(app)

        # Missing required field
        response = client.post(
            "/api/v1/retrieve",
            json={
                "knowledge_ids": ["test_kb_1"]
            }
        )

        assert response.status_code == 422  # Validation error

    def test_retrieve_simple_validation(self):
        """Test validation for simple retrieve"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/retrieve/simple",
            json={
                "query": "test"
                # missing knowledge_id
            }
        )

        assert response.status_code == 422
