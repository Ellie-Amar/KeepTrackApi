from __future__ import annotations

from uuid import uuid4
from httpx import AsyncClient
import pytest
import pytest_asyncio

from tests.support.db import clear_tasks


@pytest_asyncio.fixture(autouse=True)
async def clean_tasks_table():
    """Ensure DB is clean before each test."""
    await clear_tasks()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_then_list_ok(client: AsyncClient):
    """Create a task then list all tasks; the created one must appear."""
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


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_empty_label_task_ko(client: AsyncClient):
    """Creating a task with empty label should fail validation (422)."""
    payload = {
        "userId": str(uuid4()),
        "label": "",  # invalid: min length 1
    }

    r = await client.post("/v1/tasks", json=payload)
    assert r.status_code == 422, r.text
