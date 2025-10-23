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


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_by_id_ok(client: AsyncClient):
    """After creating a task, GET by id should return 200 with the same task."""
    payload = {
        "userId": str(uuid4()),
        "label": "SQL Read",
        "note": "chapter 1",
        "category": "personal",
    }
    r_create = await client.post("/v1/tasks", json=payload)
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_get = await client.get(f"/v1/tasks/{created['id']}")
    assert r_get.status_code == 200, r_get.text
    body = r_get.json()
    assert body["id"] == created["id"]
    assert body["label"] == "SQL Read"
    assert "createdAt" in body and "updatedAt" in body


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_by_id_not_found_ko(client: AsyncClient):
    """GET by id should return 404 for an unknown id."""
    r = await client.get(f"/v1/tasks/{uuid4()}")
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Task not found"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_partial_update_ok(client: AsyncClient):
    """PATCH should update only provided fields and return 200."""
    r_create = await client.post(
        "/v1/tasks",
        json={"userId": str(uuid4()), "label": "Before", "note": "n"},
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = await client.patch(
        f"/v1/tasks/{created['id']}",
        json={"label": "After", "note": "updated"},
    )
    assert r_patch.status_code == 200, r_patch.text
    body = r_patch.json()
    assert body["label"] == "After"
    assert body["note"] == "updated"
    assert body["updatedAt"] != created["updatedAt"]


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_not_found_ko(client: AsyncClient):
    """PATCH unknown id should return 404."""
    r = await client.patch(f"/v1/tasks/{uuid4()}", json={"label": "Nope"})
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Task not found"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_validation_label_empty_ko(client: AsyncClient):
    """PATCH with label='' should fail validation (422)."""
    r_create = await client.post(
        "/v1/tasks",
        json={"userId": str(uuid4()), "label": "Ok"},
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = await client.patch(f"/v1/tasks/{created['id']}", json={"label": ""})
    assert r_patch.status_code == 422, r_patch.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_delete_task_then_not_found_ko(client: AsyncClient):
    """DELETE should return 204 once, then 404 if called again."""
    r_create = await client.post(
        "/v1/tasks",
        json={"userId": str(uuid4()), "label": "ToDelete"},
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_del1 = await client.delete(f"/v1/tasks/{created['id']}")
    assert r_del1.status_code == 204, r_del1.text

    r_del2 = await client.delete(f"/v1/tasks/{created['id']}")
    assert r_del2.status_code == 404, r_del2.text
    assert r_del2.json()["detail"] == "Task not found"
