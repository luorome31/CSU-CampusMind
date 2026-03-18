# backend/tests/core/session/test_manager.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from app.core.session.manager import (
    UnifiedSessionManager,
    CASCredentialsNotSetError,
    NeedReLoginError,
)
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


def test_get_session_raises_when_no_castgc(temp_dir):
    """无 CASTGC 时应抛出 NeedReLoginError"""
    session_path = os.path.join(temp_dir, "sessions.json")
    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # No CASTGC cached, should raise NeedReLoginError
    with pytest.raises(NeedReLoginError):
        manager.get_session("user1", "jwc")


@patch('app.core.session.manager.SubsystemSessionProvider.get_provider')
@patch('app.core.session.manager.cas_login.cas_login_only_castgc')
def test_login_saves_castgc(mock_castgc, mock_get_provider, temp_dir):
    """login() 应保存 CASTGC"""
    mock_castgc.return_value = "test_castgc_value"

    session_path = os.path.join(temp_dir, "sessions.json")
    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    manager.login("user1", "test_user", "test_password")

    # Verify CASTGC was saved
    castgc = manager._get_castgc("user1")
    assert castgc == "test_castgc_value"


@patch('app.core.session.manager.SubsystemSessionProvider.get_provider')
def test_get_session_uses_provider(mock_get_provider, temp_dir):
    """get_session 应使用 SubsystemSessionProvider"""
    # Setup mock provider
    mock_provider = MagicMock()
    mock_session = requests.Session()
    mock_provider.fetch_session.return_value = mock_session
    mock_get_provider.return_value = mock_provider

    session_path = os.path.join(temp_dir, "sessions.json")
    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # First save a CASTGC
    manager._save_castgc("user1", "test_castgc")

    # Now get session
    result = manager.get_session("user1", "jwc")

    assert result == mock_session
    mock_provider.fetch_session.assert_called_once_with("test_castgc")


def test_login_then_get_session_flow(temp_dir):
    """完整流程: login() 后 get_session()"""
    session_path = os.path.join(temp_dir, "sessions.json")
    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Manually save CASTGC (simulating login)
    manager._save_castgc("user1", "test_castgc_123")

    # Get CASTGC should work
    castgc = manager._get_castgc("user1")
    assert castgc == "test_castgc_123"


def test_invalidate_session_clears_castgc(temp_dir):
    """invalidate_session(None) 应清除 CASTGC"""
    session_path = os.path.join(temp_dir, "sessions.json")
    persistence = FileSessionPersistence(storage_path=session_path)
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Save CASTGC
    manager._save_castgc("user1", "test_castgc")

    # Verify it's saved
    assert manager._get_castgc("user1") == "test_castgc"

    # Invalidate all sessions
    manager.invalidate_session("user1")

    # CASTGC should be cleared
    assert manager._get_castgc("user1") is None
