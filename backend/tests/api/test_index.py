"""
Index API tests
"""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


class TestIndexAPI:
    """Tests for Index API endpoints"""

    @pytest.fixture
    def mock_indexer(self):
        """Mock indexer service"""
        with patch("app.api.v1.index.indexer") as mock:
            mock.index_content = AsyncMock(return_value={
                "success": True,
                "chunk_count": 10,
                "file_id": "file_123"
            })
            mock.index_from_oss = AsyncMock(return_value={
                "success": True,
                "chunk_count": 5,
                "file_id": "file_456"
            })
            yield mock

    def test_create_index(self, mock_indexer):
        """Test POST /api/v1/index/create"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/index/create",
            json={
                "content": "Test content to index",
                "knowledge_id": "test_kb_1",
                "source_name": "test.txt",
                "enable_vector": True,
                "enable_keyword": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["chunk_count"] == 10
        assert data["knowledge_id"] == "test_kb_1"

    def test_create_index_no_vector(self, mock_indexer):
        """Test POST /api/v1/index/create without vector storage"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/index/create",
            json={
                "content": "Test content",
                "knowledge_id": "test_kb_1",
                "enable_vector": False,
                "enable_keyword": True
            }
        )

        assert response.status_code == 200

    def test_index_from_oss(self, mock_indexer):
        """Test POST /api/v1/index/create-from-oss"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/index/create-from-oss",
            json={
                "oss_url": "https://oss.example.com/file.txt",
                "knowledge_id": "test_kb_1",
                "enable_vector": True,
                "enable_keyword": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["chunk_count"] == 5

    def test_create_index_failure(self, mock_indexer):
        """Test index failure handling"""
        from app.main import app
        client = TestClient(app)

        mock_indexer.index_content.return_value = {
            "success": False,
            "error": "Indexing failed"
        }

        response = client.post(
            "/api/v1/index/create",
            json={
                "content": "Test content",
                "knowledge_id": "test_kb_1"
            }
        )

        # FastAPI will still return 200 but with success=False
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
