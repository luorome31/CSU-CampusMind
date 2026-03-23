"""
Knowledge File Verification API tests
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.database.models.knowledge_file import FileStatus

class TestKnowledgeFileVerificationAPI:
    @pytest.fixture
    def mock_service(self):
        with patch("app.api.v1.knowledge_file.KnowledgeFileService") as mock:
            mock_file = MagicMock()
            mock_file.id = "file_123"
            mock_file.oss_url = "http://minio:9000/campusmind/crawl/test_file.md"
            mock_file.object_name = "crawl/test_file.md"
            mock_file.status = FileStatus.PENDING_VERIFY
            mock_file.knowledge_id = "test_kb_1"
            mock_file.file_name = "test_file.md"
            mock_file.user_id = "test_user"
            
            mock.get_knowledge_file.return_value = mock_file
            mock.update_file_status.return_value = True
            yield mock

    @pytest.fixture
    def mock_storage(self):
        with patch("app.api.v1.knowledge_file.storage_client") as mock:
            mock.get_content.return_value = b"# Hello Raw Content"
            mock.upload_content.return_value = None
            yield mock
            
    @pytest.fixture
    def mock_indexer(self):
        with patch("app.services.rag.indexer.indexer") as mock:
            mock.index_content = AsyncMock(return_value={"success": True})
            yield mock

    @pytest.fixture
    def mock_db_session(self):
        with patch("app.api.v1.knowledge_file.Session") as mock_session:
            mock_db_file = MagicMock()
            mock_session.return_value.__enter__.return_value.exec.return_value.first.return_value = mock_db_file
            yield mock_session

    def test_get_content(self, mock_service, mock_storage, mock_auth):
        from app.main import app
        client = TestClient(app)
        response = client.get("/api/v1/knowledge_file/file_123/content")
        assert response.status_code == 200
        assert response.text == "# Hello Raw Content"
        
        # Verify object name parsing
        mock_storage.get_content.assert_called_with("crawl/test_file.md")

    def test_update_content(self, mock_service, mock_storage, mock_db_session, mock_auth):
        from app.main import app
        client = TestClient(app)
        
        payload = {"content": "Updated Output Content"}
        response = client.put("/api/v1/knowledge_file/file_123/content", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "Content updated and file verified"}
        
        # Verify OSS upload
        mock_storage.upload_content.assert_called_with("crawl/test_file.md", b"Updated Output Content")

    def test_trigger_index(self, mock_service, mock_storage, mock_indexer, mock_auth):
        from app.main import app
        client = TestClient(app)
        
        # Using a valid status for indexing
        mock_service.get_knowledge_file.return_value.status = FileStatus.VERIFIED
        
        payload = {
            "enable_vector": True,
            "enable_keyword": False
        }
        response = client.post("/api/v1/knowledge_file/file_123/trigger_index", json=payload)
        
        assert response.status_code == 200
        assert response.json() == {"success": True, "message": "File indexed successfully"}
        
        mock_storage.get_content.assert_called_with("crawl/test_file.md")
        mock_indexer.index_content.assert_called_once()
