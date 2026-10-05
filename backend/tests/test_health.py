import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint returns API information."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "RiskZen API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "operational"
    assert "docs" in data
    assert "health" in data


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test the health check endpoint returns 200 and component statuses."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "database" in data
    assert "vector_extension" in data
    assert "llm_provider" in data
    assert data["database"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_versioned_health_check_endpoint(client: AsyncClient):
    """Test the /api/v1/health endpoint returns 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"]["status"] == "healthy"
