"""
E2E Test Configuration and Shared Fixtures

Provides common fixtures for all E2E tests including:
- API client configuration
- Authentication fixtures
- Test data management
- Logging setup
"""
import os
import sys
import pytest
import logging
import requests
from typing import Generator, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Ensure backend path is available
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Configure logging for E2E tests
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
e2e_logger = logging.getLogger("e2e")


# ============================================================================
# Configuration
# ============================================================================

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
API_V1 = f"{BASE_URL}/api/v1"

# Test user credentials from .env (for authenticated tests)
TEST_CAS_USERNAME = os.getenv("CAS_USERNAME")
TEST_CAS_PASSWORD = os.getenv("CAS_PASSWORD")

# Default test user ID
DEFAULT_TEST_USER = "e2e_test_user"


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class SSEEvent:
    """Parsed SSE event from streaming response"""
    type: str
    timestamp: float
    data: dict

    @classmethod
    def from_dict(cls, data: dict) -> "SSEEvent":
        return cls(
            type=data.get("type", "unknown"),
            timestamp=data.get("timestamp", 0.0),
            data=data.get("data", {})
        )


@dataclass
class StreamingResponse:
    """Accumulated streaming response data"""
    success: bool
    events: list = field(default_factory=list)
    response_chunks: list = field(default_factory=list)
    accumulated_text: str = ""
    dialog_id: Optional[str] = None
    error: Optional[str] = None

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def chunk_count(self) -> int:
        return len(self.response_chunks)

    def get_tool_events(self) -> list:
        """Get all tool-related events"""
        return [e for e in self.events if e.type == "event"]

    def get_tool_names_called(self) -> list:
        """Extract tool names from START events"""
        tools = []
        for event in self.events:
            if event.type == "event" and event.data.get("status") == "START":
                title = event.data.get("title", "")
                if "执行工具:" in title:
                    tool_name = title.replace("执行工具:", "").strip()
                    tools.append(tool_name)
        return tools


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for API requests"""
    return BASE_URL


@pytest.fixture(scope="session")
def api_v1() -> str:
    """API v1 prefix"""
    return API_V1


@pytest.fixture(scope="session")
def test_credentials() -> dict:
    """Load test credentials from .env"""
    if not TEST_CAS_USERNAME or not TEST_CAS_PASSWORD:
        e2e_logger.warning(
            "CAS credentials not found in .env - authenticated tests will be skipped"
        )
    return {
        "username": TEST_CAS_USERNAME,
        "password": TEST_CAS_PASSWORD
    }


@pytest.fixture(scope="session")
def http_session() -> Generator[requests.Session, None, None]:
    """Reusable HTTP session for tests"""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield session
    session.close()


@pytest.fixture
def authenticated_token(http_session: requests.Session, test_credentials: dict) -> Optional[str]:
    """
    Get authentication token for tests.

    Skips if credentials not available in .env.
    Returns None if login fails.
    """
    if not test_credentials["username"] or not test_credentials["password"]:
        pytest.skip("CAS credentials not available in .env")

    try:
        response = http_session.post(
            f"{API_V1}/auth/login",
            json={
                "username": test_credentials["username"],
                "password": test_credentials["password"]
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            e2e_logger.info(f"Authenticated as user: {data.get('user_id')}")
            return data.get("token")
        else:
            e2e_logger.warning(
                f"Authentication failed: {response.status_code} - {response.text}"
            )
            return None

    except requests.exceptions.RequestException as e:
        e2e_logger.error(f"Authentication request failed: {e}")
        return None


@pytest.fixture
def auth_headers(authenticated_token: Optional[str]) -> dict:
    """Get authorization headers for authenticated requests"""
    if authenticated_token:
        return {"Authorization": f"Bearer {authenticated_token}"}
    return {}


# ============================================================================
# Streaming Response Helper
# ============================================================================

def parse_sse_stream(response: requests.Response) -> StreamingResponse:
    """
    Parse SSE stream from response and accumulate data.

    Args:
        response: requests.Response with streaming=True

    Returns:
        StreamingResponse with accumulated events and text
    """
    result = StreamingResponse(success=True)
    buffer = ""

    # Try to get dialog_id from headers
    result.dialog_id = response.headers.get("X-Dialog-ID")

    try:
        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
            if chunk:
                buffer += chunk

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()

                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            import json
                            event_data = json.loads(data_str)
                            event = SSEEvent.from_dict(event_data)
                            result.events.append(event)

                            if event.type == "response_chunk":
                                chunk_text = event.data.get("chunk", "")
                                result.response_chunks.append(chunk_text)
                                result.accumulated_text += chunk_text

                        except json.JSONDecodeError:
                            e2e_logger.debug(f"Failed to parse SSE data: {data_str[:100]}")

        # Handle any remaining buffer
        if buffer.strip():
            e2e_logger.debug(f"Remaining buffer: {buffer[:200]}")

    except Exception as e:
        result.success = False
        result.error = str(e)
        e2e_logger.error(f"Error parsing SSE stream: {e}")

    return result


# ============================================================================
# Pytest Markers
# ============================================================================

def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "e2e: end-to-end tests")
    config.addinivalue_line("markers", "auth_required: tests requiring authentication")
    config.addinivalue_line("markers", "slow: slow running tests")
    config.addinivalue_line("markers", "public_tools: tests for public (non-auth) tools")
    config.addinivalue_line("markers", "auth_tools: tests for authenticated tools")
