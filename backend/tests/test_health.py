"""Health endpoint tests for TransKeep"""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Test health check endpoints"""

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns ok"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "TransKeep" in data["message"]

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test basic health endpoint"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "TransKeep Backend"
        assert "version" in data

    @pytest.mark.asyncio
    async def test_detailed_health_endpoint(self, client: AsyncClient):
        """Test detailed health endpoint with component checks"""
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "components" in data
        assert "database" in data["components"]
        assert "redis" in data["components"]

        # Database should be healthy in test environment
        assert data["components"]["database"]["status"] == "healthy"
        assert data["components"]["database"]["type"] == "postgresql"

