"""
Crawl API tests
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


class TestCrawlAPI:
    """Tests for Crawl API endpoints"""

    @pytest.fixture
    def mock_crawl_service(self):
        """Mock crawl service"""
        with patch("app.api.v1.crawl.crawl_service") as mock:
            mock.crawl_and_prepare_for_storage = AsyncMock(return_value={
                "success": True,
                "content": "Crawled web content",
                "storage_key": "test/key",
                "metadata": {"title": "Example Domain"}
            })
            yield mock

    @pytest.fixture
    def mock_storage(self):
        """Mock storage client"""
        with patch("app.api.v1.crawl.storage_client") as mock:
            mock.upload_content = lambda key, content: f"https://oss.example.com/{key}"
            yield mock

    @pytest.fixture
    def mock_knowledge_file_service(self):
        """Mock knowledge file service"""
        with patch("app.api.v1.crawl.KnowledgeFileService") as mock:
            mock_kf = MagicMock()
            mock_kf.id = "test_file_id"
            mock.create_knowledge_file.return_value = mock_kf
            mock.update_file_status.return_value = True
            yield mock

    def test_crawl_url(self, mock_crawl_service, mock_storage, mock_auth):
        """Test POST /api/v1/crawl/create"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/crawl/create",
            json={
                "url": "https://example.com",
                "store_to_oss": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_crawl_url_no_storage(self, mock_crawl_service, mock_auth):
        """Test crawl without OSS storage"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/crawl/create",
            json={
                "url": "https://example.com",
                "store_to_oss": False
            }
        )

        assert response.status_code == 200

    def test_crawl_and_index(self, mock_crawl_service, mock_storage, mock_knowledge_file_service, mock_auth):
        """Test POST /api/v1/crawl/create-and-index"""
        from app.main import app
        client = TestClient(app)

        with patch("app.services.rag.indexer.indexer.index_content", new_callable=AsyncMock) as mock_index:
            mock_index.return_value = {"success": True, "chunk_count": 10}
            
            response = client.post(
                "/api/v1/crawl/create-and-index",
                json={
                    "url": "https://example.com",
                    "knowledge_id": "test_kb_1",
                    "enable_vector": True,
                    "enable_keyword": True
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["file_id"] == "test_file_id"
            mock_index.assert_called_once()

    def test_crawl_batch(self, mock_crawl_service, mock_storage, mock_auth):
        """Test POST /api/v1/crawl/batch"""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/crawl/batch",
            json={
                "urls": ["https://example.com", "https://example.org"],
                "store_to_oss": True
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "task_id" in data
        assert data["status"] == "processing"

    def test_list_crawl_tasks(self, mock_crawl_service, mock_auth):
        """Test GET /api/v1/crawl/tasks"""
        from app.main import app
        client = TestClient(app)

        with patch("app.api.v1.crawl.CrawlTaskService.list_tasks") as mock_list:
            mock_list.return_value = []
            response = client.get("/api/v1/crawl/tasks")
            assert response.status_code == 200
            assert response.json() == []
            mock_list.assert_called_once_with("test_user")
