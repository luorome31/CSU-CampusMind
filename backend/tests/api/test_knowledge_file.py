"""
Knowledge File API tests
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


class TestKnowledgeFileAPI:
    """Tests for Knowledge File API endpoints"""

    @pytest.fixture
    def mock_service(self):
        """Mock KnowledgeFileService"""
        with patch("app.api.v1.knowledge_file.KnowledgeFileService") as mock:
            # Mock file object
            mock_file = MagicMock()
            mock_file.id = "file_123"
            mock_file.file_name = "test.txt"
            mock_file.knowledge_id = "test_kb_1"
            mock_file.user_id = "test_user"
            mock_file.status = "success"
            mock_file.oss_url = "https://oss.example.com/test.txt"
            mock_file.file_size = 1024
            mock_file.to_dict.return_value = {
                "id": "file_123",
                "file_name": "test.txt",
                "knowledge_id": "test_kb_1",
                "user_id": "test_user",
                "status": "success",
                "oss_url": "https://oss.example.com/test.txt",
                "file_size": 1024,
                "create_time": "2024-01-01T00:00:00",
                "update_time": "2024-01-01T00:00:00"
            }

            mock.create_knowledge_file.return_value = mock_file
            mock.get_knowledge_file.return_value = mock_file
            mock.list_knowledge_files.return_value = [mock_file]
            mock.update_file_status.return_value = True
            mock.delete_knowledge_file.return_value = True

            yield mock

    def test_create_knowledge_file(self, mock_service, mock_auth):
        """Test POST /api/v1/knowledge_file/create"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/knowledge_file/create",
            json={
                "file_name": "test.txt",
                "knowledge_id": "test_kb_1",
                "oss_url": "https://oss.example.com/test.txt",
                "file_size": 1024
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "file_123"
        assert data["file_name"] == "test.txt"

    def test_get_knowledge_file(self, mock_service, mock_auth):
        """Test GET /api/v1/knowledge_file/{file_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/v1/knowledge_file/file_123")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "file_123"

    def test_get_knowledge_file_not_found(self, mock_service, mock_auth):
        """Test GET /api/v1/knowledge_file/{file_id} - not found"""
        from app.main import app
        client = TestClient(app)

        mock_service.get_knowledge_file.return_value = None

        response = client.get("/api/v1/knowledge_file/nonexistent")

        assert response.status_code == 404

    def test_list_knowledge_files(self, mock_service, mock_auth):
        """Test GET /api/v1/knowledge/{knowledge_id}/files"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/v1/knowledge/test_kb_1/files")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

    def test_update_file_status(self, mock_service, mock_auth):
        """Test PATCH /api/v1/knowledge_file/{file_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.patch(
            "/api/v1/knowledge_file/file_123",
            json={
                "status": "success"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_delete_knowledge_file(self, mock_service, mock_auth):
        """Test DELETE /api/v1/knowledge_file/{file_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.delete("/api/v1/knowledge_file/file_123")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
