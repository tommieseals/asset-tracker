"""Tests for asset endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
def auth_headers():
    """Get auth headers for testing"""
    return {"Authorization": "Bearer test-token"}

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}

@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Asset Inventory Tracker" in data["message"]
