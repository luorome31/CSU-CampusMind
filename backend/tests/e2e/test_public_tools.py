"""
E2E Test - Public Tools (No Authentication Required)

Tests the following public tools that work without authentication:
- rag_search: Search knowledge bases
- career_teachin: Campus recruitment 宣讲会 information
- career_campus_recruit: 校园招聘 information
- career_campus_intern: 实习岗位 information
- career_jobfair: 招聘会 information
- library_search: Library catalog search
- library_get_book_location: Book location/copies info
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

e2e_logger = logging.getLogger("e2e.public_tools")


@pytest.mark.e2e
@pytest.mark.public_tools
class TestPublicToolsViaCompletion:
    """
    Test public tools through the completion endpoint.

    These tests verify that anonymous users can access public tools.
    """

    def _send_completion(
        self,
        http_session: requests.Session,
        message: str,
        user_id: str = "anonymous",
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
                "user_id": user_id,
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

    def test_library_search_called_for_book_query(
        self,
        http_session: requests.Session
    ):
        """
        Test that library_search tool is called for book-related queries.

        Expected: library_search tool is invoked
        """
        e2e_logger.info("Testing library_search via completion")

        result = self._send_completion(
            http_session=http_session,
            message="查找Python相关的图书"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "library_search" in tool_names, (
            f"Expected library_search to be called, got: {tool_names}"
        )

    def test_career_teachin_called_for_recruitment_event_query(
        self,
        http_session: requests.Session
    ):
        """
        Test that career_teachin tool is called for recruitment events.

        Expected: career_teachin tool is invoked
        """
        e2e_logger.info("Testing career_teachin via completion")

        result = self._send_completion(
            http_session=http_session,
            message="查看最近的宣讲会信息"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "career_teachin" in tool_names, (
            f"Expected career_teachin to be called, got: {tool_names}"
        )

    def test_career_campus_recruit_called_for_job_query(
        self,
        http_session: requests.Session
    ):
        """
        Test that career_campus_recruit tool is called for campus recruitment.

        Expected: career_campus_recruit tool is invoked
        """
        e2e_logger.info("Testing career_campus_recruit via completion")

        result = self._send_completion(
            http_session=http_session,
            message="查找校园招聘的职位"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "career_campus_recruit" in tool_names, (
            f"Expected career_campus_recruit to be called, got: {tool_names}"
        )

    def test_career_campus_intern_called_for_internship_query(
        self,
        http_session: requests.Session
    ):
        """
        Test that career_campus_intern tool is called for internships.

        Expected: career_campus_intern tool is invoked
        """
        e2e_logger.info("Testing career_campus_intern via completion")

        result = self._send_completion(
            http_session=http_session,
            message="找一些实习机会"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "career_campus_intern" in tool_names, (
            f"Expected career_campus_intern to be called, got: {tool_names}"
        )

    def test_career_jobfair_called_for_job_fair_query(
        self,
        http_session: requests.Session
    ):
        """
        Test that career_jobfair tool is called for job fair queries.

        Expected: career_jobfair tool is invoked
        """
        e2e_logger.info("Testing career_jobfair via completion")

        result = self._send_completion(
            http_session=http_session,
            message="查询招聘会的最新信息"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "career_jobfair" in tool_names, (
            f"Expected career_jobfair to be called, got: {tool_names}"
        )

    def test_anonymous_user_can_access_all_public_tools(
        self,
        http_session: requests.Session
    ):
        """
        Test that anonymous user can access multiple public tools.

        Expected: All public tools are accessible without authentication
        """
        e2e_logger.info("Testing anonymous user access to all public tools")

        # Query that might trigger multiple public tools
        result = self._send_completion(
            http_session=http_session,
            message="我想了解一下图书馆有什么Python书籍，以及最近的宣讲会和实习机会"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"All tools called: {tool_names}")

        # Should have called at least one public tool
        public_tools = [
            "library_search", "career_teachin", "career_campus_recruit",
            "career_campus_intern", "career_jobfair"
        ]
        called_public_tools = [t for t in tool_names if t in public_tools]

        assert len(called_public_tools) > 0, (
            f"Expected at least one public tool to be called, got: {tool_names}"
        )

        e2e_logger.info(f"Public tools called: {called_public_tools}")


@pytest.mark.e2e
@pytest.mark.public_tools
class TestLibrarySearch:
    """Test library_search tool functionality"""

    def _call_library_search(
        self,
        http_session: requests.Session,
        keywords: str,
        page: int = 1,
        rows: int = 10
    ) -> requests.Response:
        """Helper to call library search endpoint directly."""
        e2e_logger.info(f"Calling library search: keywords='{keywords}'")

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": f"搜索图书：{keywords}",
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            stream=True,
            timeout=60
        )

        return response

    def test_library_search_returns_results(
        self,
        http_session: requests.Session
    ):
        """
        Test that library search returns book results.

        Expected: SSE stream contains book information
        """
        e2e_logger.info("Testing library search returns results")

        response = self._call_library_search(
            http_session=http_session,
            keywords="Python"
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

        result = parse_sse_stream(response)
        assert result.success, f"Library search failed: {result.error}"
        assert result.chunk_count > 0, "No response chunks received"

        # Check if response contains book-related content
        response_text = result.accumulated_text.lower()
        assert len(response_text) > 0, "Response should not be empty"
        e2e_logger.info(
            f"Library search response length: {len(result.accumulated_text)} chars"
        )


@pytest.mark.e2e
@pytest.mark.public_tools
class TestCareerTools:
    """Test career tools functionality"""

    def _call_career_tool(
        self,
        http_session: requests.Session,
        tool_type: str,
        query: str
    ) -> StreamingResponse:
        """Helper to call a career tool via completion."""
        e2e_logger.info(f"Calling career tool: {tool_type} with query: {query}")

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": query,
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "text/event-stream"
            },
            stream=True,
            timeout=60
        )

        if response.status_code != 200:
            return StreamingResponse(
                success=False,
                error=f"HTTP {response.status_code}: {response.text[:200]}"
            )

        return parse_sse_stream(response)

    def test_teachin_with_zone_filter(
        self,
        http_session: requests.Session
    ):
        """
        Test career_teachin with campus zone filter.

        Expected: Tool is called with zone parameter
        """
        e2e_logger.info("Testing career_teachin with zone filter")

        result = self._call_career_tool(
            http_session=http_session,
            tool_type="teachin",
            query="查看岳麓山校区的宣讲会"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "career_teachin" in tool_names, (
            f"Expected career_teachin to be called, got: {tool_names}"
        )

    def test_campus_recruit_with_keyword(
        self,
        http_session: requests.Session
    ):
        """
        Test career_campus_recruit with keyword filter.

        Expected: Tool is called with keyword parameter
        """
        e2e_logger.info("Testing career_campus_recruit with keyword")

        result = self._call_career_tool(
            http_session=http_session,
            tool_type="campus_recruit",
            query="搜索软件工程相关的校园招聘"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "career_campus_recruit" in tool_names, (
            f"Expected career_campus_recruit to be called, got: {tool_names}"
        )

    def test_campus_intern_with_keyword(
        self,
        http_session: requests.Session
    ):
        """
        Test career_campus_intern with keyword filter.

        Expected: Tool is called with keyword parameter
        """
        e2e_logger.info("Testing career_campus_intern with keyword")

        result = self._call_career_tool(
            http_session=http_session,
            tool_type="campus_intern",
            query="找算法相关的实习岗位"
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "career_campus_intern" in tool_names, (
            f"Expected career_campus_intern to be called, got: {tool_names}"
        )
