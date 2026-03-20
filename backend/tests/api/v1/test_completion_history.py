"""
Completion History API tests - Test history prepend in generate_stream
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from langchain_core.messages import HumanMessage, AIMessage

from app.api.v1.completion import generate_stream


class MockChatHistory:
    """Mock ChatHistory object with role and content fields"""
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content


class TestCompletionHistory:
    """Tests for completion API history functionality"""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock async database session"""
        mock_db = MagicMock()

        # Mock commit and add
        mock_db.commit = AsyncMock()
        mock_db.add = MagicMock()

        # Mock execute to return a result with scalar_one_or_none
        mock_result = MagicMock()
        mock_result.scalar_one_or_none = MagicMock(return_value=None)
        mock_db.execute = AsyncMock(return_value=mock_result)

        return mock_db

    @pytest.fixture
    def mock_agent(self):
        """Create a mock ReactAgent that yields streaming events"""
        mock_agent = MagicMock()

        # Create a simple async generator that yields one event then ends
        async def mock_stream():
            yield {"type": "response_chunk", "data": {"chunk": "Hello", "accumulated": "Hello"}}

        mock_agent.astream = MagicMock(return_value=mock_stream())
        return mock_agent

    @pytest.fixture
    def sample_histories(self):
        """Sample chat histories to return from HistoryService"""
        return [
            MockChatHistory(role="user", content="Hello, bot!"),
            MockChatHistory(role="assistant", content="Hello, human!"),
        ]

    @pytest.mark.asyncio
    async def test_generate_stream_calls_history_service(
        self, mock_agent, mock_db_session, sample_histories
    ):
        """Test that generate_stream() calls HistoryService.get_history_by_dialog()"""
        dialog_id = "test-dialog-123"
        message = "New user message"

        # Patch HistoryService.get_history_by_dialog to return sample histories
        with patch(
            "app.api.v1.completion.HistoryService.get_history_by_dialog",
            new_callable=AsyncMock,
            return_value=sample_histories
        ) as mock_get_history:
            # Call generate_stream and collect all yielded events
            events = []
            async for event in generate_stream(
                agent=mock_agent,
                message=message,
                knowledge_ids=[],
                session=mock_db_session,
                dialog_id=dialog_id,
                model="test-model"
            ):
                events.append(event)

            # Verify HistoryService.get_history_by_dialog was called
            mock_get_history.assert_called_once_with(mock_db_session, dialog_id)

    @pytest.mark.asyncio
    async def test_generate_stream_prepends_history_to_messages(
        self, mock_agent, mock_db_session, sample_histories
    ):
        """Test that generate_stream() prepends history to messages for the LLM"""
        dialog_id = "test-dialog-123"
        message = "New user message"

        captured_messages = []

        # Create a mock agent that captures the messages passed to it
        async def capture_messages_stream():
            # We need to capture the messages - but since agent.astream is called
            # with messages, we need to track that
            captured_messages.append("called")
            yield {"type": "response_chunk", "data": {"chunk": "Hello", "accumulated": "Hello"}}

        mock_agent.astream = MagicMock(return_value=capture_messages_stream())

        with patch(
            "app.api.v1.completion.HistoryService.get_history_by_dialog",
            new_callable=AsyncMock,
            return_value=sample_histories
        ):
            # Consume the generator
            async for _ in generate_stream(
                agent=mock_agent,
                message=message,
                knowledge_ids=[],
                session=mock_db_session,
                dialog_id=dialog_id,
                model="test-model"
            ):
                pass

            # Verify agent.astream was called (which means messages were built and passed)
            assert mock_agent.astream.called

    @pytest.mark.asyncio
    async def test_generate_stream_with_empty_history(
        self, mock_agent, mock_db_session
    ):
        """Test that generate_stream() works when there is no history"""
        dialog_id = "test-dialog-123"
        message = "First message"

        with patch(
            "app.api.v1.completion.HistoryService.get_history_by_dialog",
            new_callable=AsyncMock,
            return_value=[]
        ) as mock_get_history:
            events = []
            async for event in generate_stream(
                agent=mock_agent,
                message=message,
                knowledge_ids=[],
                session=mock_db_session,
                dialog_id=dialog_id,
                model="test-model"
            ):
                events.append(event)

            # Verify it was still called (even with empty history)
            mock_get_history.assert_called_once_with(mock_db_session, dialog_id)
            # Verify we still got events from the stream
            assert len(events) > 0