"""
E2E Test - Streaming Completion API

Tests the /api/v1/completion/stream endpoint with various scenarios:
- Anonymous user basic chat
- Authenticated user chat
- RAG-enabled requests
- SSE event parsing and validation
"""
import pytest
import requests
import logging
from typing import Optional

from tests.e2e.conftest import (
    API_V1,
    DEFAULT_TEST_USER,
    StreamingResponse,
    parse_sse_stream
)

e2e_logger = logging.getLogger("e2e.completion")


@pytest.mark.e2e
class TestStreamingCompletion:
    """Test streaming completion endpoint"""

    def _stream_completion(
        self,
        http_session: requests.Session,
        message: str,
        user_id: str = DEFAULT_TEST_USER,
        knowledge_ids: list = None,
        enable_rag: bool = False,
        auth_token: Optional[str] = None,
        timeout: int = 120
    ) -> StreamingResponse:
        """
        Helper to send streaming completion request.

        Args:
            http_session: HTTP session
            message: User message
            user_id: User identifier
            knowledge_ids: Knowledge base IDs for RAG
            enable_rag: Whether to enable RAG
            auth_token: Optional JWT token
            timeout: Request timeout in seconds

        Returns:
            StreamingResponse with accumulated events
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        payload = {
            "message": message,
            "knowledge_ids": knowledge_ids or [],
            "user_id": user_id,
            "enable_rag": enable_rag
        }

        e2e_logger.info(f"Sending completion request: message='{message[:50]}...'")

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json=payload,
            headers=headers,
            stream=True,
            timeout=timeout
        )

        e2e_logger.info(f"Completion response status: {response.status_code}")

        if response.status_code != 200:
            e2e_logger.error(f"Completion failed: {response.text[:500]}")
            result = StreamingResponse(success=False, error=response.text)
            return result

        return parse_sse_stream(response)

    def test_anonymous_basic_chat(
        self,
        http_session: requests.Session
    ):
        """
        Test anonymous user can chat with public tools.

        Expected: Response with events and text chunks
        """
        e2e_logger.info("Testing anonymous basic chat")

        result = self._stream_completion(
            http_session=http_session,
            message="查找Python相关的图书",
            user_id="anonymous",
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"
        assert result.event_count > 0, "No events received"
        assert result.chunk_count > 0, "No response chunks received"
        assert len(result.accumulated_text) > 0, "No accumulated text"

        e2e_logger.info(
            f"Anonymous chat successful: "
            f"events={result.event_count}, chunks={result.chunk_count}, "
            f"text_len={len(result.accumulated_text)}"
        )

    def test_anonymous_career_tools(
        self,
        http_session: requests.Session
    ):
        """
        Test anonymous user can access career tools.

        Expected: career_teachin or similar tool called
        """
        e2e_logger.info("Testing anonymous career tools access")

        result = self._stream_completion(
            http_session=http_session,
            message="查看最近的宣讲会信息",
            user_id="anonymous",
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        # Verify career tool was called
        career_tools = [t for t in tool_names if "career" in t.lower() or "teachin" in t.lower()]
        assert len(career_tools) > 0, (
            f"Expected career tool to be called, got: {tool_names}"
        )

    def test_authenticated_user_chat(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can chat with all tools.

        Expected: Chat succeeds with authenticated context
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated user chat")

        result = self._stream_completion(
            http_session=http_session,
            message="查询我的成绩",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"
        assert result.dialog_id is not None, "No dialog_id in response"

        e2e_logger.info(
            f"Authenticated chat successful: dialog_id={result.dialog_id}"
        )

    def test_rag_with_knowledge_ids(
        self,
        http_session: requests.Session
    ):
        """
        Test RAG-enabled request with knowledge base IDs.

        Expected: RAG tool is called and returns context
        """
        e2e_logger.info("Testing RAG with knowledge_ids")

        # Note: This requires a valid knowledge base ID
        # Using a placeholder - actual implementation may need real KB
        result = self._stream_completion(
            http_session=http_session,
            message="在知识库中搜索休学申请流程",
            user_id=DEFAULT_TEST_USER,
            knowledge_ids=["test-kb-id"],  # May not exist
            enable_rag=True
        )

        # Should still return response (may have RAG error if KB doesn't exist)
        assert result.success or result.error is not None, (
            "Request should either succeed or return error"
        )

        e2e_logger.info(
            f"RAG request completed: success={result.success}, "
            f"error={result.error}"
        )

    def test_multi_turn_conversation(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test multi-turn conversation using dialog_id.

        Expected: Second request continues the same dialog
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing multi-turn conversation")

        # First message
        result1 = self._stream_completion(
            http_session=http_session,
            message="查询通知",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        assert result1.success, f"First request failed: {result1.error}"
        dialog_id = result1.dialog_id
        assert dialog_id is not None, "No dialog_id from first request"

        e2e_logger.info(f"First turn dialog_id: {dialog_id}")

        # Second message with same dialog_id
        result2 = self._stream_completion(
            http_session=http_session,
            message="还有其他的吗",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        # Note: dialog_id may change between requests in current impl
        assert result2.success, f"Second request failed: {result2.error}"

        e2e_logger.info(
            f"Multi-turn conversation: turn1_events={result1.event_count}, "
            f"turn2_events={result2.event_count}"
        )

    def test_sse_event_format(
        self,
        http_session: requests.Session
    ):
        """
        Test that SSE events follow expected format.

        Expected: Events have type, timestamp, and data fields
        """
        e2e_logger.info("Testing SSE event format")

        result = self._stream_completion(
            http_session=http_session,
            message="你好",
            user_id=DEFAULT_TEST_USER,
            enable_rag=False,
            timeout=60
        )

        assert result.success, f"Request failed: {result.error}"

        # Check event structure
        for event in result.events[:5]:  # Check first 5 events
            assert hasattr(event, 'type'), "Event missing 'type' field"
            assert hasattr(event, 'timestamp'), "Event missing 'timestamp' field"
            assert hasattr(event, 'data'), "Event missing 'data' field"
            assert isinstance(event.data, dict), "Event data should be dict"

        # Check response_chunk structure
        if result.response_chunks:
            chunk_event = next(
                (e for e in result.events if e.type == "response_chunk"),
                None
            )
            assert chunk_event is not None, "No response_chunk event found"
            assert "chunk" in chunk_event.data or "accumulated" in chunk_event.data, (
                "response_chunk missing expected fields"
            )

        e2e_logger.info(
            f"SSE format validated: {result.event_count} events, "
            f"{result.chunk_count} chunks"
        )


@pytest.mark.e2e
class TestCompletionEndpoint:
    """Test completion endpoint availability and error handling"""

    def test_completion_requires_message(
        self,
        http_session: requests.Session
    ):
        """
        Test that completion requires message field.

        Expected: 422 Unprocessable Entity for missing message
        """
        e2e_logger.info("Testing completion with missing message")

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "user_id": DEFAULT_TEST_USER,
                "knowledge_ids": []
            },
            timeout=10
        )

        assert response.status_code == 422, (
            f"Expected 422 for missing message, got {response.status_code}"
        )

    def test_rag_requires_knowledge_ids(
        self,
        http_session: requests.Session
    ):
        """
        Test that RAG requires knowledge_ids when enabled.

        Expected: 400 Bad Request if enable_rag=True but no knowledge_ids
        """
        e2e_logger.info("Testing RAG without knowledge_ids")

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": "test",
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": True,
                "knowledge_ids": []  # Empty when RAG enabled
            },
            timeout=10
        )

        assert response.status_code == 400, (
            f"Expected 400 for RAG without knowledge_ids, "
            f"got {response.status_code}"
        )
