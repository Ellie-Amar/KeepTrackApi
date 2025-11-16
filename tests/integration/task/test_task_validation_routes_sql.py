from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.support.db import clear_tasks


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    await clear_tasks()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_task_validation_returns_display_name_ok(
    client: AsyncClient, auth_factory
):
    ctx = await auth_factory(display_name="SQL User")
    task_resp = await client.post(
        "/v1/tasks",
        json={"label": "Task"},
        headers=ctx.headers,
    )
    task_id = task_resp.json()["id"]

    resp = await client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "first"},
        headers=ctx.headers,
    )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["note"] == "first"
    assert body["user"]["displayName"] == "SQL User"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_validation_updates_note_ok(
    client: AsyncClient, auth_factory
):
    ctx = await auth_factory(display_name="SQL User")
    task = (
        await client.post("/v1/tasks", json={"label": "Task"}, headers=ctx.headers)
    ).json()
    created = (
        await client.post(
            f"/v1/tasks/{task['id']}/validations",
            json={"note": "old"},
            headers=ctx.headers,
        )
    ).json()

    resp = await client.patch(
        f"/v1/tasks/{task['id']}/validations/{created['id']}",
        json={"note": "updated"},
        headers=ctx.headers,
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["note"] == "updated"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_patch_task_validation_other_user_ko(
    client: AsyncClient, auth_factory
):
    owner = await auth_factory(display_name="Owner")
    other = await auth_factory(display_name="Other")
    task = (
        await client.post("/v1/tasks", json={"label": "Task"}, headers=owner.headers)
    ).json()
    created = (
        await client.post(
            f"/v1/tasks/{task['id']}/validations",
            json={"note": "protected"},
            headers=owner.headers,
        )
    ).json()

    resp = await client.patch(
        f"/v1/tasks/{task['id']}/validations/{created['id']}",
        json={"note": "intrude"},
        headers=other.headers,
    )

    assert resp.status_code == 404, resp.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_delete_task_validation_then_missing_ok(
    client: AsyncClient, auth_factory
):
    ctx = await auth_factory(display_name="SQL User")
    task = (
        await client.post("/v1/tasks", json={"label": "Task"}, headers=ctx.headers)
    ).json()
    created = (
        await client.post(
            f"/v1/tasks/{task['id']}/validations",
            json={"note": "temp"},
            headers=ctx.headers,
        )
    ).json()

    delete_resp = await client.delete(
        f"/v1/tasks/{task['id']}/validations/{created['id']}",
        headers=ctx.headers,
    )
    assert delete_resp.status_code == 204, delete_resp.text

    list_resp = await client.get("/v1/tasks", headers=ctx.headers)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert all(len(task["validations"]) == 0 for task in tasks)


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_delete_task_validation_other_user_ko(
    client: AsyncClient, auth_factory
):
    owner = await auth_factory(display_name="Owner")
    other = await auth_factory(display_name="Other")
    task = (
        await client.post("/v1/tasks", json={"label": "Task"}, headers=owner.headers)
    ).json()
    created = (
        await client.post(
            f"/v1/tasks/{task['id']}/validations",
            json={"note": "protected"},
            headers=owner.headers,
        )
    ).json()

    resp = await client.delete(
        f"/v1/tasks/{task['id']}/validations/{created['id']}",
        headers=other.headers,
    )

    assert resp.status_code == 404, resp.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_tasks_endpoint_includes_validation_user_ok(
    client: AsyncClient, auth_factory
):
    ctx = await auth_factory(display_name="SQL User")
    task = (
        await client.post("/v1/tasks", json={"label": "Task"}, headers=ctx.headers)
    ).json()
    await client.post(
        f"/v1/tasks/{task['id']}/validations",
        json={"note": "history"},
        headers=ctx.headers,
    )

    resp = await client.get("/v1/tasks", headers=ctx.headers)

    assert resp.status_code == 200
    tasks = resp.json()
    assert len(tasks[0]["validations"]) == 1
    validation = tasks[0]["validations"][0]
    assert validation["note"] == "history"
    assert validation["user"]["displayName"] == "SQL User"
