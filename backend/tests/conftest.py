"""
Pytest configuration and fixtures for CampusMind backend tests
"""
import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set test environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_campusmind.db")
os.environ.setdefault("TESTING", "true")

@pytest.fixture(autouse=True, scope="session")
def setup_test_db():
    """Initialize test database tables"""
    from app.database.session import create_db_and_tables
    # Import models to ensure they are registered with SQLModel
    from app.database.models.crawl_task import CrawlTask  # noqa: F401
    from app.database.models.knowledge import KnowledgeBase  # noqa: F401
    from app.database.models.knowledge_file import KnowledgeFile  # noqa: F401
    from app.database.models.dialog import Dialog  # noqa: F401
    from app.database.models.chat_history import ChatHistory  # noqa: F401
    from app.database.models.user import User  # noqa: F401
    from app.database.models.tool_definition import ToolDefinition  # noqa: F401
    from app.database.models.tool_call_log import ToolCallLog  # noqa: F401
    create_db_and_tables()


@pytest.fixture
def mock_auth():
    """Override auth dependencies for testing"""
    from app.main import app
    from app.api.dependencies import get_current_user, get_optional_user
    
    async def override_get_current_user():
        return {"user_id": "test_user", "username": "test_user"}
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_optional_user] = override_get_current_user
    yield {"user_id": "test_user", "username": "test_user"}
    app.dependency_overrides.clear()


@pytest.fixture
def mock_knowledge_service():
    """Mock KnowledgeService for testing"""

    mock = MagicMock()
    mock.create_knowledge = MagicMock(return_value=MagicMock(
        id="test_kb_1",
        name="Test Knowledge",
        description="Test description",
        user_id="test_user",
        to_dict=lambda: {
            "id": "test_kb_1",
            "name": "Test Knowledge",
            "description": "Test description",
            "user_id": "test_user",
            "create_time": "2024-01-01T00:00:00",
            "update_time": "2024-01-01T00:00:00"
        }
    ))
    mock.get_knowledge = MagicMock(return_value=MagicMock(
        id="test_kb_1",
        name="Test Knowledge",
        description="Test description",
        user_id="test_user",
        to_dict=lambda: {
            "id": "test_kb_1",
            "name": "Test Knowledge",
            "description": "Test description",
            "user_id": "test_user",
            "create_time": "2024-01-01T00:00:00",
            "update_time": "2024-01-01T00:00:00"
        }
    ))
    mock.list_knowledge_by_user = MagicMock(return_value=[
        MagicMock(
            id="test_kb_1",
            name="Test Knowledge",
            description="Test description",
            user_id="test_user",
            to_dict=lambda: {
                "id": "test_kb_1",
                "name": "Test Knowledge",
                "description": "Test description",
                "user_id": "test_user",
                "create_time": "2024-01-01T00:00:00",
                "update_time": "2024-01-01T00:00:00"
            }
        )
    ])
    mock.delete_knowledge = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_rag_handler():
    """Mock RAG handler for testing"""

    mock = MagicMock()
    mock.retrieve_with_sources = AsyncMock(return_value={
        "context": "Test context from retrieval",
        "sources": [
            {"content": "Source 1", "score": 0.9},
            {"content": "Source 2", "score": 0.8}
        ]
    })
    mock.index_content = AsyncMock(return_value={
        "success": True,
        "chunk_count": 5
    })
    return mock


@pytest.fixture
def mock_crawl_service():
    """Mock crawl service for testing"""

    mock = MagicMock()
    mock.crawl_url = AsyncMock(return_value={
        "success": True,
        "task_id": "crawl_task_123",
        "status": "pending"
    })
    mock.get_crawl_result = AsyncMock(return_value={
        "task_id": "crawl_task_123",
        "status": "completed",
        "content": "Crawled content"
    })
    return mock


@pytest.fixture
def sample_knowledge_request():
    """Sample knowledge creation request data"""
    return {
        "name": "Test Knowledge Base",
        "description": "A test knowledge base",
        "user_id": "test_user"
    }


@pytest.fixture
def sample_retrieve_request():
    """Sample retrieval request data"""
    return {
        "query": "What is CampusMind?",
        "knowledge_ids": ["test_kb_1"],
        "enable_vector": True,
        "enable_keyword": True,
        "top_k": 5,
        "min_score": 0.0
    }


@pytest.fixture
def sample_crawl_request():
    """Sample crawl request data"""
    return {
        "url": "https://example.com",
        "knowledge_id": "test_kb_1"
    }


# === Core Module Fixtures ===

@pytest.fixture
def mock_langchain_model():
    """Mock LangChain chat model for ReactAgent testing"""
    from unittest.mock import AsyncMock

    mock_model = MagicMock()

    # Mock AIMessage with tool_calls
    mock_response = MagicMock()
    mock_response.tool_calls = [
        {"name": "test_tool", "args": {"query": "test"}, "id": "call_123"}
    ]
    mock_response.content = "Test response"

    mock_model.bind_tools = MagicMock(return_value=MagicMock(
        ainvoke=AsyncMock(return_value=mock_response)
    ))

    return mock_model


@pytest.fixture
def mock_base_tool():
    """Mock LangChain BaseTool for testing"""

    tool = MagicMock()
    tool.name = "test_tool"
    tool.description = "A test tool"
    tool.coroutine = True
    tool.ainvoke = AsyncMock(return_value="Tool execution result")
    tool.invoke = MagicMock(return_value="Tool execution result")

    return tool


@pytest.fixture
def mock_stream_writer():
    """Mock StreamWriter for testing"""

    writer = MagicMock()
    writer_calls = []

    def capture_call(data):
        writer_calls.append(data)

    writer.side_effect = capture_call
    writer.calls = writer_calls

    return writer
