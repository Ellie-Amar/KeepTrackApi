from uuid import uuid4
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

import pytest_asyncio
from tests.support.db import clear_tasks


@pytest_asyncio.fixture(autouse=True)
async def clean_tasks_table():
    """Ensure the tasks table is empty before each SQL test (same event loop)."""
    await clear_tasks()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_then_list_ok():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "userId": str(uuid4()),
            "label": "Read a book",
            "note": "20 minutes",
            "category": "personal",
        }

        r = await client.post("/v1/tasks", json=payload)
        assert r.status_code == 201, r.text
        created = r.json()
        assert created["label"] == "Read a book"
        assert "id" in created

        r2 = await client.get("/v1/tasks")
        assert r2.status_code == 200, r2.text
        items = r2.json()
        assert any(it["id"] == created["id"] for it in items)
