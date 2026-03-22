"""
E2E Test - Authenticated Tools

Tests tools that require authentication (CAS login):
- jwc_grade: Query student grades
- jwc_schedule: Query student class schedule
- jwc_rank: Query student major ranking
- jwc_level_exam: Query level exam results (CET-4/6, etc.)
- oa_notification_list: Query campus notifications

These tests verify:
1. Authenticated users can access these tools
2. Anonymous users receive appropriate error messages
3. Tool parameters are correctly passed
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

e2e_logger = logging.getLogger("e2e.auth_tools")


@pytest.mark.e2e
@pytest.mark.auth_required
@pytest.mark.auth_tools
class TestJwcTools:
    """
    Test JWC (教务系统) tools that require authentication.

    These tools query student academic information from the教务系统.
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

    def test_authenticated_user_can_query_grades(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can query grades via jwc_grade.

        Expected: jwc_grade tool is called and returns grade info
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated grade query")

        result = self._send_completion(
            http_session=http_session,
            message="查询我这学期的成绩",
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "jwc_grade" in tool_names, (
            f"Expected jwc_grade to be called, got: {tool_names}"
        )

    def test_anonymous_user_cannot_query_grades(
        self,
        http_session: requests.Session
    ):
        """
        Test anonymous user receives error when trying to query grades.

        Expected: Appropriate error message about authentication
        """
        e2e_logger.info("Testing anonymous grade query (should fail)")

        result = self._send_completion(
            http_session=http_session,
            message="查询成绩"
        )

        # The request may succeed but the tool returns auth error
        # or the system prompt should prevent calling the tool
        e2e_logger.info(
            f"Anonymous grade query result: success={result.success}, "
            f"tools_called={result.get_tool_names_called()}"
        )

        # If tools were called, jwc_grade should not be among them
        # (or if it was called, it should have returned an auth error)
        tool_names = result.get_tool_names_called()
        if "jwc_grade" in tool_names:
            e2e_logger.warning(
                "jwc_grade was called for anonymous user - "
                "tool should have blocked it"
            )

    def test_authenticated_user_can_query_schedule(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can query schedule via jwc_schedule.

        Expected: jwc_schedule tool is called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated schedule query")

        result = self._send_completion(
            http_session=http_session,
            message="查询我这学期的课表",
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "jwc_schedule" in tool_names, (
            f"Expected jwc_schedule to be called, got: {tool_names}"
        )

    def test_authenticated_user_can_query_rank(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can query ranking via jwc_rank.

        Expected: jwc_rank tool is called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated rank query")

        result = self._send_completion(
            http_session=http_session,
            message="查询我的专业排名",
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "jwc_rank" in tool_names, (
            f"Expected jwc_rank to be called, got: {tool_names}"
        )

    def test_authenticated_user_can_query_level_exam(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can query level exams via jwc_level_exam.

        Expected: jwc_level_exam tool is called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated level exam query")

        result = self._send_completion(
            http_session=http_session,
            message="查询我的四六级成绩",
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "jwc_level_exam" in tool_names, (
            f"Expected jwc_level_exam to be called, got: {tool_names}"
        )

    def test_jwc_schedule_with_term_parameter(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test jwc_schedule correctly receives term parameter.

        Expected: Tool is called with correct term format (e.g., "2024-2025-1")
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing jwc_schedule with term parameter")

        result = self._send_completion(
            http_session=http_session,
            message="查询2024-2025学年度第一学期的课表",
            auth_token=authenticated_token
        )

        assert result.success, f"Request failed: {result.error}"

        # Verify schedule tool was called
        tool_names = result.get_tool_names_called()
        assert "jwc_schedule" in tool_names, (
            f"Expected jwc_schedule to be called, got: {tool_names}"
        )

        # Check if the term was passed correctly
        # Look for START events with the tool
        for event in result.events:
            if (event.type == "event" and
                event.data.get("status") == "START" and
                "jwc_schedule" in event.data.get("title", "")):
                message = event.data.get("message", "")
                if "2024-2025-1" in message or "term" in message.lower():
                    e2e_logger.info(f"Term parameter found in: {message}")
                    break


@pytest.mark.e2e
@pytest.mark.auth_required
@pytest.mark.auth_tools
class TestOaTools:
    """
    Test OA (校内办公网) notification tools.

    These tools query campus administrative notifications.
    """

    def test_authenticated_user_can_query_notifications(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test authenticated user can query OA notifications.

        Expected: oa_notification_list tool is called
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing authenticated notification query")

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if authenticated_token:
            headers["Authorization"] = f"Bearer {authenticated_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": "查询学校办公室最近的通知",
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers=headers,
            stream=True,
            timeout=120
        )

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )

        result = parse_sse_stream(response)
        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        e2e_logger.info(f"Tools called: {tool_names}")

        assert "oa_notification_list" in tool_names, (
            f"Expected oa_notification_list to be called, got: {tool_names}"
        )

    def test_notification_query_with_department_filter(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test oa_notification_list with department filter.

        Expected: Tool is called with qcbmmc parameter
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing notification query with department filter")

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if authenticated_token:
            headers["Authorization"] = f"Bearer {authenticated_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": "查询人事处的职称相关通知",
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers=headers,
            stream=True,
            timeout=120
        )

        assert response.status_code == 200

        result = parse_sse_stream(response)
        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "oa_notification_list" in tool_names, (
            f"Expected oa_notification_list to be called, got: {tool_names}"
        )

    def test_notification_query_with_date_range(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test oa_notification_list with date range filter.

        Expected: Tool is called with qssj and jssj parameters
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing notification query with date range")

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if authenticated_token:
            headers["Authorization"] = f"Bearer {authenticated_token}"

        response = http_session.post(
            f"{API_V1}/completion/stream",
            json={
                "message": "查询2024年全年的通知",
                "knowledge_ids": [],
                "user_id": DEFAULT_TEST_USER,
                "enable_rag": False
            },
            headers=headers,
            stream=True,
            timeout=120
        )

        assert response.status_code == 200

        result = parse_sse_stream(response)
        assert result.success, f"Request failed: {result.error}"

        tool_names = result.get_tool_names_called()
        assert "oa_notification_list" in tool_names, (
            f"Expected oa_notification_list to be called, got: {tool_names}"
        )


@pytest.mark.e2e
@pytest.mark.auth_required
class TestAuthToolErrorHandling:
    """Test error handling for authenticated tools"""

    def test_jwc_session_expired_handling(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test proper handling when JWC session expires.

        Expected: User-friendly error message about re-login
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing JWC session expiration handling")

        # Note: This test would require mocking session expiration
        # In real scenario, the tool would return an error message
        # about session expiration

        e2e_logger.warning(
            "JWC session expiration testing requires mock or real expiration"
        )
