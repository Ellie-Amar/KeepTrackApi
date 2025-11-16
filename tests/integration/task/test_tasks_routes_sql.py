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


async def _create_task(client: AsyncClient, headers, label: str = "Task") -> dict:
    response = await client.post(
        "/v1/tasks",
        json={"label": label},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


async def _create_validation(
    client: AsyncClient, task_id: str, headers, note: str = "note"
) -> dict:
    response = await client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": note},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_then_list_ok(client: AsyncClient, auth_factory):
    """Create a task then list all tasks; the created one must appear."""
    ctx = await auth_factory()
    payload = {
        "label": "Read a book",
        "note": "20 minutes",
        "category": "personal",
    }

    r = await client.post("/v1/tasks", json=payload, headers=ctx.headers)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["label"] == "Read a book"
    assert "id" in created
    assert created["ownerId"] == ctx.user["id"]

    r2 = await client.get("/v1/tasks", headers=ctx.headers)
    assert r2.status_code == 200, r2.text
    items = r2.json()
    assert any(it["id"] == created["id"] for it in items)


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_list_tasks_includes_validations_ok(
    client: AsyncClient, auth_factory
):
    ctx = await auth_factory(display_name="ListUser")
    task = await _create_task(client, ctx.headers)
    await _create_validation(client, task["id"], ctx.headers, note="sql note")

    resp = await client.get("/v1/tasks", headers=ctx.headers)

    assert resp.status_code == 200, resp.text
    items = resp.json()
    assert len(items[0]["validations"]) == 1
    assert items[0]["validations"][0]["note"] == "sql note"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_list_tasks_validations_other_user_ko(
    client: AsyncClient, auth_factory
):
    owner = await auth_factory(email=f"owner-{uuid4()}@example.com")
    other = await auth_factory(email=f"other-{uuid4()}@example.com")
    task = await _create_task(client, owner.headers)
    await _create_validation(client, task["id"], owner.headers, note="private")

    resp = await client.get("/v1/tasks", headers=other.headers)

    assert resp.status_code == 200, resp.text
    assert resp.json() == []


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_empty_label_task_ko(client: AsyncClient, auth_factory):
    """Creating a task with empty label should fail validation (422)."""
    ctx = await auth_factory()
    payload = {
        "label": "",  # invalid: min length 1
    }

    r = await client.post("/v1/tasks", json=payload, headers=ctx.headers)
    assert r.status_code == 422, r.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_by_id_ok(client: AsyncClient, auth_factory):
    """After creating a task, GET by id should return 200 with the same task."""
    ctx = await auth_factory()
    payload = {
        "label": "SQL Read",
        "note": "chapter 1",
        "category": "personal",
    }
    r_create = await client.post("/v1/tasks", json=payload, headers=ctx.headers)
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_get = await client.get(f"/v1/tasks/{created['id']}", headers=ctx.headers)
    assert r_get.status_code == 200, r_get.text
    body = r_get.json()
    assert body["id"] == created["id"]
    assert body["label"] == "SQL Read"
    assert "createdAt" in body and "updatedAt" in body


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_includes_validations_ok(client: AsyncClient, auth_factory):
    ctx = await auth_factory(display_name="Reader")
    task = await _create_task(client, ctx.headers)
    await _create_validation(client, task["id"], ctx.headers, note="history")

    resp = await client.get(f"/v1/tasks/{task['id']}", headers=ctx.headers)

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert len(body["validations"]) == 1
    assert body["validations"][0]["note"] == "history"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_validations_other_user_ko(
    client: AsyncClient, auth_factory
):
    owner = await auth_factory(email=f"owner-{uuid4()}@example.com")
    other = await auth_factory(email=f"other-{uuid4()}@example.com")
    task = await _create_task(client, owner.headers)
    await _create_validation(client, task["id"], owner.headers, note="private")

    resp = await client.get(f"/v1/tasks/{task['id']}", headers=other.headers)

    assert resp.status_code == 404, resp.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_get_task_by_id_not_found_ko(client: AsyncClient, auth_factory):
    """GET by id should return 404 for an unknown id."""
    ctx = await auth_factory()
    r = await client.get(f"/v1/tasks/{uuid4()}", headers=ctx.headers)
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Task not found"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_partial_update_ok(client: AsyncClient, auth_factory):
    """PATCH should update only provided fields and return 200."""
    ctx = await auth_factory()
    r_create = await client.post(
        "/v1/tasks",
        json={"label": "Before", "note": "n"},
        headers=ctx.headers,
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = await client.patch(
        f"/v1/tasks/{created['id']}",
        json={"label": "After", "note": "updated"},
        headers=ctx.headers,
    )
    assert r_patch.status_code == 200, r_patch.text
    body = r_patch.json()
    assert body["label"] == "After"
    assert body["note"] == "updated"
    assert body["updatedAt"] != created["updatedAt"]


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_not_found_ko(client: AsyncClient, auth_factory):
    """PATCH unknown id should return 404."""
    ctx = await auth_factory()
    r = await client.patch(
        f"/v1/tasks/{uuid4()}",
        json={"label": "Nope"},
        headers=ctx.headers,
    )
    assert r.status_code == 404, r.text
    assert r.json()["detail"] == "Task not found"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_validation_label_empty_ko(
    client: AsyncClient, auth_factory
):
    """PATCH with label='' should fail validation (422)."""
    ctx = await auth_factory()
    r_create = await client.post(
        "/v1/tasks",
        json={"label": "Ok"},
        headers=ctx.headers,
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = await client.patch(
        f"/v1/tasks/{created['id']}",
        json={"label": ""},
        headers=ctx.headers,
    )
    assert r_patch.status_code == 422, r_patch.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_delete_task_then_not_found_ko(client: AsyncClient, auth_factory):
    """DELETE should return 204 once, then 404 if called again."""
    ctx = await auth_factory()
    r_create = await client.post(
        "/v1/tasks",
        json={"label": "ToDelete"},
        headers=ctx.headers,
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_del1 = await client.delete(f"/v1/tasks/{created['id']}", headers=ctx.headers)
    assert r_del1.status_code == 204, r_del1.text

    r_del2 = await client.delete(f"/v1/tasks/{created['id']}", headers=ctx.headers)
    assert r_del2.status_code == 404, r_del2.text
    assert r_del2.json()["detail"] == "Task not found"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_task_uses_authenticated_owner(
    client: AsyncClient, auth_factory
):
    """OwnerId should be derived from the authenticated user."""
    ctx = await auth_factory(email=f"auth-owner-{uuid4()}@example.com")

    response = await client.post(
        "/v1/tasks",
        json={"label": "First task"},
        headers=ctx.headers,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["ownerId"] == ctx.user["id"]
    assert body["label"] == "First task"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_task_without_token_unauthorized(client: AsyncClient):
    """Creating a task without credentials should fail with 401."""
    r = await client.post("/v1/tasks", json={"label": "Should fail"})
    assert r.status_code == 401, r.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_list_only_returns_user_tasks(client: AsyncClient, auth_factory):
    """A user should not see tasks owned by others."""
    ctx_owner = await auth_factory(email=f"owner-{uuid4()}@example.com")
    ctx_other = await auth_factory(email=f"other-{uuid4()}@example.com")

    await client.post(
        "/v1/tasks",
        json={"label": "Owner task"},
        headers=ctx_owner.headers,
    )
    await client.post(
        "/v1/tasks",
        json={"label": "Other task"},
        headers=ctx_other.headers,
    )

    response = await client.get("/v1/tasks", headers=ctx_other.headers)
    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items) == 1
    assert items[0]["label"] == "Other task"
    assert items[0]["ownerId"] == ctx_other.user["id"]


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_access_denied_for_other_user(client: AsyncClient, auth_factory):
    """Another user must get 404 when accessing someone else's task."""
    ctx_owner = await auth_factory(email=f"owner-access-{uuid4()}@example.com")
    ctx_other = await auth_factory(email=f"other-access-{uuid4()}@example.com")

    create_resp = await client.post(
        "/v1/tasks",
        json={"label": "Owner secret"},
        headers=ctx_owner.headers,
    )
    assert create_resp.status_code == 201, create_resp.text
    task = create_resp.json()

    for method in ("get", "patch", "delete"):
        if method == "get":
            resp = await client.get(
                f"/v1/tasks/{task['id']}", headers=ctx_other.headers
            )
        elif method == "patch":
            resp = await client.patch(
                f"/v1/tasks/{task['id']}",
                json={"label": "Hack"},
                headers=ctx_other.headers,
            )
        else:
            resp = await client.delete(
                f"/v1/tasks/{task['id']}", headers=ctx_other.headers
            )
        assert resp.status_code == 404
