"""
Integration tests: Test complete Session acquisition and tool invocation flow

This module tests:
1. SessionManager integration
2. JwcService integration
3. JWC Tools (LangChain tools) integration
"""
import pytest
import os
import tempfile
import requests
from unittest.mock import Mock, patch, MagicMock

from app.core.session import (
    UnifiedSessionManager,
    SubsystemSessionCache,
    FileSessionPersistence,
    PasswordManager,
    LoginRateLimiter,
)
from app.core.tools.jwc import JwcService, set_session_manager
from app.core.tools.jwc.tools import (
    _get_grades,
    _get_schedule,
    _set_password,
    get_session_manager as get_jwc_session_manager,
)


def create_mock_session():
    """Create a mock requests.Session."""
    session = MagicMock()
    session.cookies = MagicMock()
    session.cookies.__iter__ = MagicMock(return_value=iter([]))
    return session


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_cas_login():
    """Mock CAS login to avoid actual network calls."""
    with patch('app.core.session.cas_login.cas_login') as mock:
        mock.return_value = create_mock_session()
        yield mock


@pytest.fixture
def session_manager(temp_dir, mock_cas_login):
    """Create a SessionManager instance for testing."""
    session_path = os.path.join(temp_dir, "sessions.json")
    password_path = os.path.join(temp_dir, "passwords.json")

    persistence = FileSessionPersistence(storage_path=session_path)
    password_mgr = PasswordManager(storage_path=password_path, encryption_key="test-key-12345")
    rate_limiter = LoginRateLimiter()

    manager = UnifiedSessionManager(
        password_manager=password_mgr,
        persistence=persistence,
        rate_limiter=rate_limiter,
        ttl_seconds=60
    )

    # Set to global module
    set_session_manager(manager)

    return manager


def test_set_password_and_get(session_manager):
    """Test password set and get operations."""
    session_manager.set_password("user1", "mypassword")

    password = session_manager.get_password("user1")
    assert password == "mypassword"


def test_session_manager_integration():
    """Test SessionManager integration."""
    manager = get_jwc_session_manager()
    assert manager is not None


@patch('app.core.tools.jwc.client.JwcClient.get_grades')
def test_jwc_service_get_grades(mock_get_grades, session_manager):
    """Test JwcService.get_grades."""
    from app.core.tools.jwc.client import Grade

    # Set password first
    session_manager.set_password("user1", "testpassword")

    # Mock return data
    mock_get_grades.return_value = [
        Grade("2024-2025-1", "高等数学", "95", "4.0", "必修", "考试")
    ]

    service = JwcService(session_manager)
    grades = service.get_grades("user1")

    assert len(grades) == 1
    assert grades[0].course_name == "高等数学"
    assert grades[0].score == "95"


def test_tool_set_password(session_manager):
    """Test JwcSetPasswordTool."""
    result = _set_password("user1", "testpassword")

    assert "成功" in result
    assert session_manager.get_password("user1") == "testpassword"


@patch('app.core.tools.jwc.client.JwcClient.get_grades')
def test_tool_get_grades(mock_get_grades, session_manager):
    """Test JwcGradeTool."""
    from app.core.tools.jwc.client import Grade

    # Set password first
    session_manager.set_password("user1", "testpassword")

    mock_get_grades.return_value = [
        Grade("2024-2025-1", "数据结构", "90", "3.0", "必修", "考试")
    ]

    result = _get_grades("user1", "2024-2025-1")

    assert "数据结构" in result
    assert "90" in result


@patch('app.core.tools.jwc.client.JwcClient.get_class_schedule')
def test_tool_get_schedule(mock_get_schedule, session_manager):
    """Test JwcScheduleTool."""
    from app.core.tools.jwc.client import ClassEntry

    # Set password first
    session_manager.set_password("user1", "testpassword")

    mock_get_schedule.return_value = [
        ClassEntry("数据结构", "张三", "1-16", "A101", "周一", "1-2")
    ]

    result = _get_schedule("user1", "2024-2025-1", "1")

    assert "数据结构" in result
    assert "张三" in result
    assert "周一" in result


@patch('app.core.tools.jwc.client.JwcClient.get_rank')
def test_tool_get_rank(mock_get_rank, session_manager):
    """Test JwcRankTool."""
    from app.core.tools.jwc.client import RankEntry

    # Set password first
    session_manager.set_password("user1", "testpassword")

    mock_get_rank.return_value = [
        RankEntry("2024-2025-1", "85.5", "5/30", "82.0")
    ]

    from app.core.tools.jwc.tools import _get_rank
    result = _get_rank("user1")

    assert "5" in result  # class rank
    assert "85.5" in result  # total score


@patch('app.core.tools.jwc.client.JwcClient.get_level_exams')
def test_tool_get_level_exams(mock_get_level_exams, session_manager):
    """Test JwcLevelExamTool."""
    from app.core.tools.jwc.client import LevelExamEntry

    # Set password first
    session_manager.set_password("user1", "testpassword")

    mock_get_level_exams.return_value = [
        LevelExamEntry("大学英语四级", "425", "", "425", "C", "", "C", "2024-06-15")
    ]

    from app.core.tools.jwc.tools import _get_level_exams
    result = _get_level_exams("user1")

    assert "大学英语四级" in result
    assert "425" in result
