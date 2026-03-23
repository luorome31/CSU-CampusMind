"""
Dialog API tests
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from datetime import datetime

class TestDialogAPI:
    """Tests for Dialog API endpoints"""

    @pytest.fixture
    def mock_repo(self):
        """Mock DialogRepository"""
        with patch("app.api.v1.dialog.DialogRepository") as mock:
            # Setup mock dialog
            mock_dialog = MagicMock()
            mock_dialog.id = "test_dialog_1"
            mock_dialog.title = "Test Dialog"
            mock_dialog.updated_at = datetime.now()
            mock_dialog.to_dict.return_value = {
                "id": "test_dialog_1",
                "user_id": "test_user",
                "agent_id": None,
                "title": "Test Dialog",
                "updated_at": mock_dialog.updated_at.isoformat()
            }
            
            # Mock methods
            mock.list_user_dialogs = AsyncMock(return_value=[mock_dialog])
            mock.list_anonymous_dialogs = AsyncMock(return_value=[mock_dialog])
            mock.get_dialog_history = AsyncMock(return_value=[])
            mock.delete_dialog = AsyncMock(return_value=True)
            mock.update_dialog_title = AsyncMock(return_value=mock_dialog)
            mock.get_dialog_if_authorized = AsyncMock(return_value=mock_dialog)
            
            yield mock

    def test_list_dialogs(self, mock_repo, mock_auth):
        """Test GET /api/v1/dialogs"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/api/v1/dialogs")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "test_dialog_1"
        assert data[0]["title"] == "Test Dialog"
        mock_repo.list_user_dialogs.assert_called_once()

    def test_get_dialog_messages(self, mock_repo, mock_auth):
        """Test GET /api/v1/dialogs/{dialog_id}/messages"""
        from app.main import app
        client = TestClient(app)

        mock_msg = MagicMock()
        mock_msg.to_dict.return_value = {
            "id": "msg_1", 
            "role": "user", 
            "content": "Hello", 
            "file_url": None,
            "events": None,
            "created_at": datetime.now().isoformat()
        }
        mock_repo.get_dialog_history.return_value = [mock_msg]

        response = client.get("/api/v1/dialogs/test_dialog_1/messages")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["content"] == "Hello"
        mock_repo.get_dialog_history.assert_called_once()

    def test_update_dialog(self, mock_repo, mock_auth):
        """Test PATCH /api/v1/dialogs/{dialog_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.patch(
            "/api/v1/dialogs/test_dialog_1",
            json={"title": "New Title"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_dialog_1"
        # Check positional args or keyword args as per the call site
        mock_repo.update_dialog_title.assert_called_once()
        call_args = mock_repo.update_dialog_title.call_args
        assert call_args[0][1] == "test_dialog_1"
        assert call_args[0][2] == "New Title"
        assert call_args[0][3] == "test_user"

    def test_delete_dialog(self, mock_repo, mock_auth):
        """Test DELETE /api/v1/dialogs/{dialog_id}"""
        from app.main import app
        client = TestClient(app)

        response = client.delete("/api/v1/dialogs/test_dialog_1")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        mock_repo.delete_dialog.assert_called_once()
        call_args = mock_repo.delete_dialog.call_args
        assert call_args[0][1] == "test_dialog_1"
        assert call_args[0][2] == "test_user"
