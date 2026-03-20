"""
Tests for tool_logger decorator and context
"""
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock


class TestToolContext:
    """Tests for thread-local context functions"""

    def test_set_and_get_context(self):
        """Test setting and getting context"""
        from app.core.tools.context import set_tool_context, get_tool_context, clear_tool_context

        # Clear any existing context
        clear_tool_context()

        # Set context
        set_tool_context(user_id="user_123", dialog_id="dialog_456")
        context = get_tool_context()

        assert context["user_id"] == "user_123"
        assert context["dialog_id"] == "dialog_456"

        # Clean up
        clear_tool_context()

    def test_get_context_defaults(self):
        """Test getting context when not set returns defaults"""
        from app.core.tools.context import set_tool_context, get_tool_context, clear_tool_context

        # Ensure no context is set
        clear_tool_context()

        context = get_tool_context()

        assert context["user_id"] is None
        assert context["dialog_id"] is None

    def test_clear_context(self):
        """Test clearing context"""
        from app.core.tools.context import set_tool_context, get_tool_context, clear_tool_context

        set_tool_context(user_id="user_123", dialog_id="dialog_456")
        clear_tool_context()

        context = get_tool_context()
        assert context["user_id"] is None
        assert context["dialog_id"] is None

    def test_context_with_none_values(self):
        """Test setting context with None values"""
        from app.core.tools.context import set_tool_context, get_tool_context, clear_tool_context

        clear_tool_context()
        set_tool_context(user_id=None, dialog_id=None)

        context = get_tool_context()
        assert context["user_id"] is None
        assert context["dialog_id"] is None


class TestToolLoggerDecorator:
    """Tests for tool_logger decorator"""

    @pytest.fixture
    def mock_session_dependency(self):
        """Mock async_session_dependency"""
        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()

        async def mock_gen():
            yield mock_session

        return mock_gen

    @pytest.mark.asyncio
    async def test_decorator_logs_success(self, mock_session_dependency):
        """Test decorator logs successful tool execution"""
        from app.core.tools.context import set_tool_context, clear_tool_context

        clear_tool_context()
        set_tool_context(user_id="user_123", dialog_id="dialog_456")

        with patch("app.core.tools.decorators.async_session_dependency", mock_session_dependency):
            from app.core.tools.decorators import tool_logger

            # Create a mock tool with the decorator
            class MockTool:
                name = "mock_tool"

                @tool_logger
                async def _arun(self, tool_args):
                    return "success result"

            tool = MockTool()
            result = await tool._arun({"query": "test"})

            assert result == "success result"

        clear_tool_context()

    @pytest.mark.asyncio
    async def test_decorator_logs_failure(self, mock_session_dependency):
        """Test decorator logs failed tool execution"""
        from app.core.tools.context import set_tool_context, clear_tool_context

        clear_tool_context()
        set_tool_context(user_id="user_123", dialog_id="dialog_456")

        with patch("app.core.tools.decorators.async_session_dependency", mock_session_dependency):
            from app.core.tools.decorators import tool_logger

            class MockTool:
                name = "mock_tool"

                @tool_logger
                async def _arun(self, tool_args):
                    raise ValueError("Test error")

            tool = MockTool()

            with pytest.raises(ValueError):
                await tool._arun({"query": "test"})

        clear_tool_context()

    @pytest.mark.asyncio
    async def test_decorator_handles_anonymous_user(self, mock_session_dependency):
        """Test decorator works with anonymous user (user_id=None)"""
        from app.core.tools.context import set_tool_context, clear_tool_context

        clear_tool_context()
        set_tool_context(user_id=None, dialog_id=None)

        with patch("app.core.tools.decorators.async_session_dependency", mock_session_dependency):
            from app.core.tools.decorators import tool_logger

            class MockTool:
                name = "anon_tool"

                @tool_logger
                async def _arun(self, tool_args):
                    return "result"

            tool = MockTool()
            result = await tool._arun({"query": "test"})

            assert result == "result"

        clear_tool_context()


class TestToolCallLogModel:
    """Tests for ToolCallLog model"""

    def test_tool_call_log_optional_user_id(self):
        """Test ToolCallLog allows None user_id"""
        from app.database.models.tool_call_log import ToolCallLog

        # Create log with None user_id (anonymous)
        log = ToolCallLog(
            tool_name="test_tool",
            status="success",
            user_id=None,
            dialog_id="dialog_123"
        )

        assert log.user_id is None
        assert log.tool_name == "test_tool"
        assert log.status == "success"

    def test_tool_call_log_with_user_id(self):
        """Test ToolCallLog works with user_id"""
        from app.database.models.tool_call_log import ToolCallLog

        log = ToolCallLog(
            tool_name="test_tool",
            status="success",
            user_id="user_123",
            dialog_id="dialog_456"
        )

        assert log.user_id == "user_123"
        assert log.dialog_id == "dialog_456"

    def test_tool_call_log_to_dict(self):
        """Test ToolCallLog to_dict method"""
        from app.database.models.tool_call_log import ToolCallLog

        log = ToolCallLog(
            tool_name="test_tool",
            status="failed",
            user_id="user_123",
            dialog_id="dialog_456",
            error_message='{"error": "test"}',
            duration_ms=100
        )

        d = log.to_dict()

        assert d["tool_name"] == "test_tool"
        assert d["status"] == "failed"
        assert d["user_id"] == "user_123"
        assert d["dialog_id"] == "dialog_456"
        assert d["duration_ms"] == 100
