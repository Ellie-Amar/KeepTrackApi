import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


@pytest.mark.integration
async def test_healthcheck_returns_ok(client: AsyncClient):
    """simple sync test of healthcheck"""
    response = await client.get("/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
