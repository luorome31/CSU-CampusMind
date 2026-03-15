"""
Completion API tests
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient


class TestCompletionAPI:
    """Tests for Completion API endpoints"""

    @pytest.fixture
    def mock_deps(self):
        """Mock dependencies for completion API"""
        with patch("app.api.v1.completion.get_db_session") as mock_session, \
             patch("app.api.v1.completion.rag_handler") as mock_rag:

            # Mock database session
            mock_db = MagicMock()
            mock_session.return_value = iter([mock_db])

            # Mock RAG handler
            mock_rag.retrieve_with_sources = AsyncMock(return_value={
                "context": "Retrieved context about CampusMind.",
                "sources": [
                    {"content": "Source 1", "score": 0.9}
                ]
            })

            yield {
                "session": mock_db,
                "rag_handler": mock_rag
            }

    def test_completion_without_rag(self, mock_deps):
        """Test POST /api/v1/completion without RAG"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/completion",
            json={
                "message": "Hello, how are you?",
                "knowledge_ids": [],
                "user_id": "test_user",
                "enable_rag": False
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_completion_requires_knowledge_ids(self):
        """Test that streaming completion requires knowledge_ids when RAG is enabled"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/completion/stream",
            json={
                "message": "Hello",
                "enable_rag": True,
                "knowledge_ids": []
            }
        )

        assert response.status_code == 400

    def test_chat_endpoint(self, mock_deps):
        """Test POST /api/v1/chat"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            json={
                "query": "What is CampusMind?",
                "knowledge_id": "test_kb_1",
                "user_id": "test_user",
                "use_rag": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "dialog_id" in data

    def test_chat_without_rag(self, mock_deps):
        """Test POST /api/v1/chat without RAG"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            json={
                "query": "Hello",
                "knowledge_id": "test_kb_1",
                "user_id": "test_user",
                "use_rag": False
            }
        )

        assert response.status_code == 200
