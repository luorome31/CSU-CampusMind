# backend/tests/core/session/test_manager.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.core.session.manager import UnifiedSessionManager, CASCredentialsNotSetError
from app.core.session.cache import SubsystemSessionCache
from app.core.session.persistence import FileSessionPersistence
from app.core.session.rate_limiter import LoginRateLimiter
import requests


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_settings():
    """Mock settings to provide CAS credentials."""
    with patch('app.core.session.manager.settings') as mock:
        mock.cas_username = "test_user"
        mock.cas_password = "test_password"
        yield mock


@pytest.fixture
def manager(temp_dir, mock_settings):
    session_path = os.path.join(temp_dir, "sessions.json")

    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    return UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )


def test_get_session_no_credentials(temp_dir):
    """无 CAS 凭证时应抛出异常"""
    with patch('app.core.session.manager.settings') as mock:
        mock.cas_username = None
        mock.cas_password = None

        session_path = os.path.join(temp_dir, "sessions.json")
        persistence = FileSessionPersistence(storage_path=session_path)
        rate_limiter = LoginRateLimiter()

        manager = UnifiedSessionManager(
            persistence=persistence,
            rate_limiter=rate_limiter,
            ttl_seconds=60
        )

        with pytest.raises(CASCredentialsNotSetError):
            manager.get_session("user1", "jwc")


@patch('app.core.session.manager.cas_login.cas_login')
def test_get_session_with_credentials(mock_cas_login, manager):
    """有凭证时应调用 CAS 登录"""
    mock_session = requests.Session()
    mock_session.cookies.set("JSESSIONID", "test123")
    mock_cas_login.return_value = mock_session

    session = manager.get_session("user1", "jwc")

    assert session is not None
    mock_cas_login.assert_called_once()
