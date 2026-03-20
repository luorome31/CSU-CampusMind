"""
Knowledge API tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


# Test fixtures are in conftest.py


class TestKnowledgeAPI:
    """Tests for Knowledge API endpoints"""

    @pytest.fixture
    def mock_service(self):
        """Mock KnowledgeService"""
        with patch("app.api.v1.knowledge.KnowledgeService") as mock:
            # Setup mock create_knowledge
            mock_kb = MagicMock()
            mock_kb.id = "test_kb_1"
            mock_kb.name = "Test Knowledge"
            mock_kb.description = "Test description"
            mock_kb.user_id = "test_user"
            mock_kb.to_dict.return_value = {
                "id": "test_kb_1",
                "name": "Test Knowledge",
                "description": "Test description",
                "user_id": "test_user",
                "create_time": "2024-01-01T00:00:00",
                "update_time": "2024-01-01T00:00:00"
            }
            mock.create_knowledge.return_value = mock_kb

            # Setup mock get_knowledge
            mock.get_knowledge.return_value = mock_kb

            # Setup mock list_knowledge_by_user
            mock.list_knowledge_by_user.return_value = [mock_kb]

            # Setup mock delete_knowledge
            mock.delete_knowledge.return_value = True

            yield mock

    def test_create_knowledge(self, mock_service):
        """Test POST /api/v1/knowledge/create"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/knowledge/create",
            json={
                "name": "Test Knowledge",
                "description": "Test description",
                "user_id": "test_user"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_kb_1"
        assert data["name"] == "Test Knowledge"
        mock_service.create_knowledge.assert_called_once()

    def test_get_knowledge(self, mock_service):
        """Test GET /api/v1/knowledge/{knowledge_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/v1/knowledge/test_kb_1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_kb_1"
        mock_service.get_knowledge.assert_called_once_with("test_kb_1")

    def test_get_knowledge_not_found(self, mock_service):
        """Test GET /api/v1/knowledge/{knowledge_id} - not found"""
        from app.main import app
        client = TestClient(app)

        mock_service.get_knowledge.return_value = None

        response = client.get("/api/v1/knowledge/nonexistent")

        assert response.status_code == 404

    def test_list_knowledge(self, mock_service):
        """Test GET /api/v1/users/{user_id}/knowledge"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/v1/users/test_user/knowledge")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "test_kb_1"
        mock_service.list_knowledge_by_user.assert_called_once_with("test_user")

    def test_delete_knowledge(self, mock_service):
        """Test DELETE /api/v1/knowledge/{knowledge_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.delete("/api/v1/knowledge/test_kb_1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_service.delete_knowledge.assert_called_once_with("test_kb_1")

    def test_delete_knowledge_not_found(self, mock_service):
        """Test DELETE /api/v1/knowledge/{knowledge_id} - not found"""
        from app.main import app
        client = TestClient(app)

        mock_service.delete_knowledge.return_value = False

        response = client.delete("/api/v1/knowledge/nonexistent")

        assert response.status_code == 404
