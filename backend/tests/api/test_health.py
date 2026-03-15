"""
Health check tests
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthCheck:
    """Tests for health check endpoint"""

    def test_health_check(self):
        """Test GET /health"""
        from app.main import app
        client = TestClient(app)

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
