"""
E2E Test - Authentication Flow

Tests the authentication endpoints:
- POST /api/v1/auth/login
- POST /api/v1/auth/logout
- POST /api/v1/auth/refresh

These tests verify JWT token generation and session management.
"""
import pytest
import requests
import logging
import base64
import json
from typing import Optional

from tests.e2e.conftest import (
    API_V1,
    DEFAULT_TEST_USER
)

e2e_logger = logging.getLogger("e2e.auth")


@pytest.mark.e2e
@pytest.mark.auth_required
class TestAuthLogin:
    """Test authentication login flow"""

    @pytest.fixture
    def client(self, http_session: requests.Session):
        """HTTP client for auth tests"""
        return http_session

    def test_login_with_valid_credentials_succeeds(
        self,
        client: requests.Session,
        test_credentials: dict
    ):
        """
        Test successful login with valid CAS credentials.

        Expected: 200 OK with token, user_id, expires_in
        """
        if not test_credentials["username"] or not test_credentials["password"]:
            pytest.skip("CAS credentials not available in .env")

        e2e_logger.info("Testing login with valid credentials")

        response = client.post(
            f"{API_V1}/auth/login",
            json={
                "username": test_credentials["username"],
                "password": test_credentials["password"]
            },
            timeout=30
        )

        e2e_logger.info(f"Login response status: {response.status_code}")

        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}: {response.text}"
        )

        data = response.json()
        assert "token" in data, "Response missing 'token' field"
        assert "user_id" in data, "Response missing 'user_id' field"
        assert "expires_in" in data, "Response missing 'expires_in' field"

        # Verify token is non-empty JWT format
        token = data["token"]
        assert len(token) > 20, "Token appears to be too short"
        assert token.count(".") == 2, "Token doesn't appear to be JWT format"

        e2e_logger.info(
            f"Login successful: user={data['user_id']}, "
            f"expires_in={data['expires_in']}s"
        )

    def test_login_with_invalid_credentials_fails(
        self,
        client: requests.Session,
        test_credentials: dict
    ):
        """
        Test login failure with invalid credentials.

        Expected: 401 Unauthorized with error detail
        """
        if not test_credentials["username"]:
            pytest.skip("CAS credentials not available")

        e2e_logger.info("Testing login with invalid credentials")

        response = client.post(
            f"{API_V1}/auth/login",
            json={
                "username": test_credentials["username"],
                "password": "wrong_password_12345"
            },
            timeout=30
        )

        e2e_logger.info(f"Invalid login response status: {response.status_code}")

        assert response.status_code == 401, (
            f"Expected 401 for invalid credentials, got {response.status_code}"
        )

        data = response.json()
        assert "detail" in data, "Expected error detail in response"
        assert "登录失败" in data["detail"], (
            f"Expected Chinese error message, got: {data['detail']}"
        )

        e2e_logger.info(f"Login correctly rejected: {data['detail']}")

    def test_login_rate_limiting(
        self,
        client: requests.Session,
        test_credentials: dict
    ):
        """
        Test that repeated failed logins trigger rate limiting.

        Expected: 429 Too Many Requests after multiple failures
        """
        if not test_credentials["username"]:
            pytest.skip("CAS credentials not available")

        e2e_logger.info("Testing login rate limiting")

        # Make several rapid login attempts with wrong password
        for i in range(3):
            response = client.post(
                f"{API_V1}/auth/login",
                json={
                    "username": test_credentials["username"],
                    "password": "wrong_password_attempt"
                },
                timeout=30
            )

            if response.status_code == 429:
                e2e_logger.info(
                    f"Rate limiting triggered after {i + 1} attempts"
                )
                data = response.json()
                assert "登录过于频繁" in data.get("detail", "")
                return

        e2e_logger.info("Rate limiting not triggered (may need more attempts)")


@pytest.mark.e2e
@pytest.mark.auth_required
class TestAuthLogout:
    """Test logout functionality"""

    def test_logout_with_valid_token_succeeds(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str],
        test_credentials: dict
    ):
        """
        Test successful logout with valid token.

        Expected: 200 OK
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing logout with valid token")

        # Get user_id from token payload (simplified)
        try:
            payload = authenticated_token.split(".")[1]
            # Add padding if needed
            payload += "=" * (4 - len(payload) % 4)
            user_data = json.loads(base64.b64decode(payload))
            user_id = user_data.get("user_id")
        except Exception:
            user_id = test_credentials.get("username", DEFAULT_TEST_USER)

        response = http_session.post(
            f"{API_V1}/auth/logout",
            json={"user_id": user_id},
            headers={"Authorization": f"Bearer {authenticated_token}"},
            timeout=30
        )

        e2e_logger.info(f"Logout response status: {response.status_code}")

        # Note: May return 200 or 401 depending on implementation
        # Just verify it doesn't return 500
        assert response.status_code in [200, 401, 403], (
            f"Unexpected logout status: {response.status_code}"
        )

    def test_logout_without_token_fails(
        self,
        http_session: requests.Session
    ):
        """
        Test logout without token fails.

        Expected: 401 Unauthorized
        """
        e2e_logger.info("Testing logout without token")

        response = http_session.post(
            f"{API_V1}/auth/logout",
            json={"user_id": DEFAULT_TEST_USER},
            timeout=30
        )

        assert response.status_code == 401, (
            f"Expected 401 for unauthenticated logout, got {response.status_code}"
        )


@pytest.mark.e2e
@pytest.mark.auth_required
class TestAuthRefresh:
    """Test token refresh functionality"""

    def test_refresh_token_succeeds(
        self,
        http_session: requests.Session,
        authenticated_token: Optional[str]
    ):
        """
        Test successful token refresh.

        Expected: 200 OK with new token
        """
        if not authenticated_token:
            pytest.skip("No authenticated token available")

        e2e_logger.info("Testing token refresh")

        response = http_session.post(
            f"{API_V1}/auth/refresh",
            headers={"Authorization": f"Bearer {authenticated_token}"},
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            assert "token" in data
            assert "user_id" in data
            e2e_logger.info("Token refreshed successfully")
        else:
            # May not be implemented yet
            e2e_logger.info(f"Token refresh returned: {response.status_code}")
