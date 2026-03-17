# backend/tests/core/session/test_manager.py
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from app.core.session.manager import UnifiedSessionManager
from app.core.session.cache import SubsystemSessionCache
from app.core.session.persistence import FileSessionPersistence
from app.core.session.password import PasswordManager
from app.core.session.rate_limiter import LoginRateLimiter
import requests


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def manager(temp_dir):
    session_path = os.path.join(temp_dir, "sessions.json")
    password_path = os.path.join(temp_dir, "passwords.json")

    cache = SubsystemSessionCache(ttl_seconds=60)
    persistence = FileSessionPersistence(storage_path=session_path)
    password_mgr = PasswordManager(storage_path=password_path, encryption_key="test-key")
    rate_limiter = LoginRateLimiter()

    return UnifiedSessionManager(
        password_manager=password_mgr,
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )


def test_set_password(manager):
    manager.set_password("user1", "mypassword")
    # 验证密码已保存
    assert manager._password_manager.get_password("user1") == "mypassword"


def test_get_session_no_password(manager):
    """无密码时应抛出异常"""
    with pytest.raises(Exception, match="未设置密码"):
        manager.get_session("user1", "jwc")


@patch('app.core.session.manager.cas_login.cas_login')
def test_get_session_with_password(mock_cas_login, manager):
    """有密码时应调用 CAS 登录"""
    manager.set_password("user1", "mypassword")

    mock_session = requests.Session()
    mock_session.cookies.set("JSESSIONID", "test123")
    mock_cas_login.return_value = mock_session

    session = manager.get_session("user1", "jwc")

    assert session is not None
    mock_cas_login.assert_called_once()
