# backend/tests/core/session/test_manager.py
import pytest
import os
import tempfile
import json
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.core.session.manager import (
    UnifiedSessionManager,
    CASCredentialsNotSetError,
    NeedReLoginError,
)
from app.core.session.persistence import FileSessionPersistence
from app.core.session.rate_limiter import LoginRateLimiter
import requests


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = MagicMock()
    mock._data = {}  # In-memory storage

    async def mock_get(key):
        return mock._data.get(key)

    async def mock_setex(key, ttl, value):
        mock._data[key] = value

    async def mock_delete(key):
        mock._data.pop(key, None)

    mock.get = mock_get
    mock.setex = mock_setex
    mock.delete = mock_delete
    return mock


@pytest.fixture
def mock_persistence(mock_redis):
    """Mock persistence with Redis."""
    mock = MagicMock()
    mock._redis = mock_redis
    mock.load = AsyncMock(return_value=None)
    mock.save = AsyncMock()
    mock.invalidate = AsyncMock()
    return mock


@pytest.fixture
def mock_settings():
    """Mock settings to provide CAS credentials."""
    with patch('app.core.session.manager.settings') as mock:
        mock.cas_username = "test_user"
        mock.cas_password = "test_password"
        yield mock


@pytest.mark.asyncio
async def test_get_session_raises_when_no_castgc(mock_persistence, mock_settings):
    """无 CASTGC 时应抛出 NeedReLoginError"""
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=mock_persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # No CASTGC cached, should raise NeedReLoginError
    with pytest.raises(NeedReLoginError):
        await manager.get_session("user1", "jwc")


@pytest.mark.asyncio
@patch('app.core.session.manager.SubsystemSessionProvider.get_provider')
@patch('app.core.session.manager.cas_login.cas_login_only_castgc')
async def test_login_saves_castgc(mock_castgc, mock_get_provider, mock_persistence, mock_settings):
    """login() 应保存 CASTGC"""
    mock_castgc.return_value = "test_castgc_value"

    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=mock_persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    await manager.login("user1", "test_user", "test_password")

    # Verify CASTGC was saved
    castgc = await manager._get_castgc("user1")
    assert castgc == "test_castgc_value"


@pytest.mark.asyncio
@patch('app.core.session.manager.SubsystemSessionProvider.get_provider')
async def test_get_session_uses_provider(mock_get_provider, mock_persistence, mock_settings):
    """get_session 应使用 SubsystemSessionProvider"""
    # Setup mock provider
    mock_provider = MagicMock()
    mock_session = requests.Session()
    mock_provider.fetch_session.return_value = mock_session
    mock_get_provider.return_value = mock_provider

    # Setup mock persistence to return None (no cached session)
    mock_persistence.load = AsyncMock(return_value=None)

    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=mock_persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # First save a CASTGC
    await manager._save_castgc("user1", "test_castgc")

    # Now get session
    result = await manager.get_session("user1", "jwc")

    assert result == mock_session
    mock_provider.fetch_session.assert_called_once_with("test_castgc")


@pytest.mark.asyncio
async def test_login_then_get_session_flow(mock_persistence, mock_settings):
    """完整流程: login() 后 get_session()"""
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=mock_persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Manually save CASTGC (simulating login)
    await manager._save_castgc("user1", "test_castgc_123")

    # Get CASTGC should work
    castgc = await manager._get_castgc("user1")
    assert castgc == "test_castgc_123"


@pytest.mark.asyncio
async def test_invalidate_session_clears_castgc(mock_persistence, mock_settings):
    """invalidate_session(None) 应清除 CASTGC"""
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        persistence=mock_persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Save CASTGC
    await manager._save_castgc("user1", "test_castgc")

    # Verify it's saved
    assert await manager._get_castgc("user1") == "test_castgc"

    # Invalidate all sessions
    await manager.invalidate_session("user1")

    # CASTGC should be cleared
    assert await manager._get_castgc("user1") is None
