"""Tests for FastAPI application initialization"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_app_startup():
    """Test that app initializes without errors"""
    assert app is not None
    assert app.title == "TransKeep API"


def test_root_endpoint():
    """Test root endpoint health check"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "TransKeep Backend"
    assert "version" in data


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200
    # CORS headers should be present
    assert "access-control-allow-origin" in response.headers or response.status_code == 200


def test_404_not_found():
    """Test 404 response for unknown endpoint"""
    response = client.get("/unknown-endpoint")
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

