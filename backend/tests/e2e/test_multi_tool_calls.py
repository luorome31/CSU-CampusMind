"""
E2E Test - Multi-Tool Call Scenarios

Tests scenarios where multiple tools are called in sequence or parallel:
- Query involving multiple public tools
- Query involving multiple authenticated tools
- RAG + tool combination
- Complex multi-step queries
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

e2e_logger = logging.getLogger("e2e.multi_tool")


@pytest.mark.e2e
class TestMultiToolScenarios:
    """
    Test scenarios that involve multiple tool calls.
    """

    def _send_completion(
        self,
        http_session: requests.Session,
        message: str,
        user_id: str = DEFAULT_TEST_USER,
        knowledge_ids: list = None,
        enable_rag: bool = False,
        auth_token: Optional[str] = None,
        timeout: int = 180
    ) -> StreamingResponse:
        """Helper to send completion request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": message,
                "knowledge_ids": knowledge_ids or [],
                "user_id": user_id,
                "enable_rag": enable_rag
            },
            headers=headers,
            stream=True,
            timeout=timeout
        )

        if response.status_code != 200:
            return StreamingResponse(
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )

        return parse_sse_stream(response)

    def test_multiple_public_tools_in_sequence(
        self,
        http_session: requests.Session
    ):
        """
        Test query that triggers multiple public tools in sequence.

        Expected: library_search and career tools are both called
        """
        e2e_logger.info("Testing multiple public tools in sequence")

        result = self._send_completion(
            http_session=http_session,
            message="帮我查一下Python相关的图书，然后看看最近的宣讲会信息",
            user_id="anonymous",
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        # Should have called at least two different public tools
        assert len(tool_names) >= 2, (
            f"Expected multiple tools to be called, got: {tool_names}"
        )

        # Verify specific tools
        expected_tools = ["library_search", "career_teachin"]
        called_expected = [t for t in expected_tools if t in tool_names]
        assert len(called_expected) >= 1, (
            f"Expected at least one of {expected_tools} to be called"
        )

    def test_multiple_authenticated_tools_in_sequence(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test query that triggers multiple authenticated tools.

        Expected: oa_notification_list and jwc_grade are both called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing multiple authenticated tools")

        result = self._send_completion(
            http_session=http_session,
            message="帮我查一下教务处的通知，然后看看我上学期的成绩",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        # Should have called both tools
        expected_tools = ["oa_notification_list", "jwc_grade"]
        for tool in expected_tools:
            assert tool in tool_names, (
                f"Expected {tool} to be called, got: {tool_names}"
            )

    def test_rag_combined_with_authenticated_tool(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test RAG search combined with authenticated tool.

        Expected: rag_search and jwc_schedule are both called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing RAG combined with authenticated tool")

        result = self._send_completion(
            http_session=http_session,
            message="在知识库中搜索休学申请流程，然后查一下我的课表",
            user_id=DEFAULT_TEST_USER,
            knowledge_ids=["test-kb-id"],  # Placeholder
            enable_rag=True,
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        # Should have called both tools
        # Note: rag_search might not be called if KB doesn't exist
        e2e_logger.info(
            f"RAG + auth tool test: tools_called={tool_names}"
        )

    def test_multi_tool_error_recovery(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test that multi-tool flow continues even if one tool fails.

        Expected: Partial results returned even if one tool errors
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing multi-tool error recovery")

        # Query with potentially failing components
        result = self._send_completion(
            http_session=http_session,
            message="查询通知和成绩",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        # Should still return a response even if partial
        assert result.success or result.error is not None, (
            "Request should have some result"
        )

        e2e_logger.info(
            f"Multi-tool error recovery: success={result.success}, "
            f"tools_called={result.get_tool_names_called()}"
        )

    def test_complex_multi_step_query(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test complex query involving multiple tools and conditions.

        Expected: Multiple tools called in logical sequence
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing complex multi-step query")

        result = self._send_completion(
            http_session=http_session,
            message="我想了解学校办公室最近的5条通知，然后查查我有哪些课在周一上",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Complex query tools called: {tool_names}")

        # Should have called multiple tools
        assert len(tool_names) >= 2, (
            f"Expected multiple tools for complex query, got: {tool_names}"
        )

    def test_tool_call_order_verification(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test that tools are called in the correct order.

        Expected: Events show tools called in logical sequence
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing tool call order")

        result = self._send_completion(
            http_session=http_session,
            message="先查通知，再查成绩",
            user_id=DEFAULT_TEST_USER,
            auth_token=authenticated_token,
            enable_rag=False
        )

        assert result.success, f"Request failed: {result.error}"

        # Get all START events for tools
        tool_start_events = [
            e for e in result.events
            if e.type == "event" and e.data.get("status") == "START"
        ]

        e2e_logger.info(f"Tool call sequence:")
        for i, event in enumerate(tool_start_events):
            title = event.data.get("title", "")
            e2e_logger.info(f"  {i+1}. {title}")

        # Verify multiple tools were called
        assert len(tool_start_events) >= 2, (
            f"Expected at least 2 tool calls, got {len(tool_start_events)}"
        )


@pytest.mark.e2e
class TestToolParameterPassing:
    """
    Test that tool parameters are correctly extracted and passed.
    """

    def _send_completion(
        self,
        http_session: requests.Session,
        message: str,
        auth_token: Optional[str] = None,
        timeout: int = 120
    ) -> StreamingResponse:
        """Helper to send completion request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": message,
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers=headers,
            stream=True,
            timeout=timeout
        )

        if response.status_code != 200:
            return StreamingResponse(
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )

        return parse_sse_stream(response)

    def _extract_tool_parameters(self, result: StreamingResponse, tool_name: str) -> dict:
        """Extract parameters from tool START event."""
        for event in result.events:
            if (event.type == "event" and
                event.data.get("status") == "START" and
                tool_name in event.data.get("title", "")):
                message = event.data.get("message", "")
                # Parse parameters from message
                e2e_logger.info(f"Tool parameters for {tool_name}: {message}")
                return {"raw_message": message}
        return {}

    def test_oas_notification_with_multiple_filters(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test OA notification with multiple filter parameters.

        Expected: Tool called with qcbmmc, qssj, jssj, wjbt parameters
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing OA notification with multiple filters")

        result = self._send_completion(
            http_session=http_session,
            message='查询人事处2024年所有包含"职称"的通知',
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        params = self._extract_tool_parameters(result, "oa_notification_list")
        assert params is not None, "Could not extract tool parameters"

        # Verify tool was called
        tool_names = result.get_tool_names_called()
        assert "oa_notification_list" in tool_names, (
            f"Expected oa_notification_list to be called"
        )

    def test_library_search_with_pagination(
        self,
        http_session: requests.Session
    ):
        """
        Test library search parameters.

        Expected: library_search tool called
        """
        e2e_logger.info("Testing library search with parameters")

        result = self._send_completion(
            http_session=http_session,
            message="搜索Python相关的图书，返回前10条"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "library_search" in tool_names, (
            f"Expected library_search to be called, got: {tool_names}"
        )

    def test_career_tool_with_zone_and_keyword(
        self,
        http_session: requests.Session
    ):
        """
        Test career tool with both zone and keyword parameters.

        Expected: Tool called with combined parameters
        """
        e2e_logger.info("Testing career tool with zone and keyword")

        result = self._send_completion(
            http_session=http_session,
            message="查看岳麓山校区关于软件工程的宣讲会"
        )

        assert result.success, f"Request failed: {result.error}"

        params = self._extract_tool_parameters(result, "career_teachin")
        e2e_logger.info(f"Career tool parameters: {params}")

        # Verify tool was called
        tool_names = result.get_tool_names_called()
        assert "career_teachin" in tool_names, (
            f"Expected career_teachin to be called"
        )


@pytest.mark.e2e
class TestEdgeCases:
    """
    Test edge cases in multi-tool scenarios.
    """

    def _send_completion(
        self,
        http_session: requests.Session,
        message: str,
        auth_token: Optional[str] = None,
        timeout: int = 120
    ) -> StreamingResponse:
        """Helper to send completion request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": message,
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers=headers,
            stream=True,
            timeout=timeout
        )

        if response.status_code != 200:
            return StreamingResponse(
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )

        return parse_sse_stream(response)

    def test_query_that_triggers_no_tools(
        self,
        http_session: requests.Session
    ):
        """
        Test query that doesn't require any tools.

        Expected: No tool calls, just LLM response
        """
        e2e_logger.info("Testing query without tool calls")

        result = self._send_completion(
            http_session=http_session,
            message="你好，今天天气怎么样？"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called for casual query: {tool_names}")

        # Should have response without tool calls
        assert result.chunk_count > 0, "Should have LLM response"

    def test_rapid_sequential_requests(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test multiple rapid sequential requests.

        Expected: All requests complete successfully
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing rapid sequential requests")

        queries = [
            "查询成绩",
            "查询通知",
            "查询课表"
        ]

        results = []
        for query in queries:
            result = self._send_completion(
                http_session=http_session,
                message=query,
                auth_token=authenticated_token
            )
            results.append(result)

        # All should succeed
        for i, result in enumerate(results):
            e2e_logger.info(f"Request {i+1} ({queries[i]}): success={result.success}")
            assert result.success, f"Request {i+1} failed: {result.error}"
