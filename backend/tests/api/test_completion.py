"""
Completion API tests
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.api.v1.completion import async_session_dependency


class TestCompletionAPI:
    """Tests for Completion API endpoints"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session"""
        mock_db = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.execute = AsyncMock()
        return mock_db

    @pytest.fixture
    def mock_deps(self, mock_db_session):
        """Mock dependencies for completion API"""
        # Create mock dialog object
        mock_dialog = MagicMock()
        mock_dialog.id = "test-dialog-id"

        async def mock_get_or_create_dialog(session, dialog_id, jwt_user_id, agent_id=None):
            return (mock_dialog, True)

        with patch("app.api.v1.completion.DialogRepository.get_or_create_dialog", mock_get_or_create_dialog), \
             patch("app.api.v1.completion.rag_handler") as mock_rag:

            # Mock RAG handler
            mock_rag.retrieve_with_sources = AsyncMock(return_value={
                "context": "Retrieved context about CampusMind.",
                "sources": [
                    {"content": "Source 1", "score": 0.9}
                ]
            })

            # Override the async_session_dependency
            async def override_async_session_dependency():
                yield mock_db_session

            from app.main import app
            app.dependency_overrides[async_session_dependency] = override_async_session_dependency

            yield {
                "dialog": mock_dialog,
                "rag_handler": mock_rag
            }

            # Clean up override
            app.dependency_overrides.clear()

    def test_completion_without_rag(self, mock_deps):
        """Test POST /api/v1/completion without RAG"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/completion",
            json={
                "message": "Hello, how are you?",
                "knowledge_ids": [],
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

