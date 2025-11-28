from http import HTTPStatus
from uuid import uuid4

import pytest
import pytest_asyncio

from tests.integration.helpers.auth import create_user_and_auth
from tests.support.db import clear_tasks, clear_users


pytestmark = pytest.mark.sql


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    await clear_tasks()
    await clear_users()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_assign_and_list_sql_ok(client):
    owner = await create_user_and_auth(client, email="owner_sql@example.com")
    other = await create_user_and_auth(client, email="other_sql@example.com")

    resp = await client.post(
        "/v1/tasks",
        headers=owner.headers,
        json={"label": "demo"},
    )
    assert resp.status_code == HTTPStatus.CREATED
    task_id = resp.json()["id"]

    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        headers=owner.headers,
        json={"userEmails": [other.user["email"]]},
    )
    assert resp.status_code == HTTPStatus.CREATED

    resp = await client.get(f"/v1/tasks/{task_id}/assignees", headers=owner.headers)
    assert resp.status_code == HTTPStatus.OK
    emails = {u["email"] for u in resp.json()}
    assert emails == {owner.user["email"], other.user["email"]}


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_list_as_participant_sql_ok(client):
    owner = await create_user_and_auth(client, email="owner2_sql@example.com")
    participant = await create_user_and_auth(
        client, email="participant2_sql@example.com"
    )

    resp = await client.post(
        "/v1/tasks",
        headers=owner.headers,
        json={"label": "demo"},
    )
    task_id = resp.json()["id"]

    await client.post(
        f"/v1/tasks/{task_id}/assignees",
        headers=owner.headers,
        json={"userEmails": [participant.user["email"]]},
    )

    resp = await client.get(
        f"/v1/tasks/{task_id}/assignees", headers=participant.headers
    )
    assert resp.status_code == HTTPStatus.OK
    emails = {u["email"] for u in resp.json()}
    assert participant.user["email"] in emails


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_assign_non_owner_sql_ko(client):
    owner = await create_user_and_auth(client, email="owner3_sql@example.com")
    other = await create_user_and_auth(client, email="other3_sql@example.com")
    third = await create_user_and_auth(client, email="third3_sql@example.com")

    resp = await client.post("/v1/tasks", headers=owner.headers, json={"label": "demo"})
    task_id = resp.json()["id"]

    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        headers=other.headers,
        json={"userEmails": [third.user["email"]]},
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_assign_missing_user_sql_ko(client):
    owner = await create_user_and_auth(client, email="owner4_sql@example.com")
    resp = await client.post("/v1/tasks", headers=owner.headers, json={"label": "demo"})
    task_id = resp.json()["id"]

    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        headers=owner.headers,
        json={"userEmails": ["missing@example.com"]},
    )
    assert resp.status_code == HTTPStatus.BAD_REQUEST


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_unassign_sql_ok(client):
    owner = await create_user_and_auth(client, email="owner5_sql@example.com")
    other = await create_user_and_auth(client, email="other5_sql@example.com")

    resp = await client.post("/v1/tasks", headers=owner.headers, json={"label": "demo"})
    task_id = resp.json()["id"]

    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        headers=owner.headers,
        json={"userEmails": [other.user["email"]]},
    )
    user_id = resp.json()[0]["id"]

    resp = await client.delete(
        f"/v1/tasks/{task_id}/assignees/{user_id}", headers=owner.headers
    )
    assert resp.status_code == HTTPStatus.NO_CONTENT

    resp = await client.get(f"/v1/tasks/{task_id}/assignees", headers=owner.headers)
    emails = {u["email"] for u in resp.json()}
    assert other.user["email"] not in emails


@pytest.mark.sql
@pytest.mark.asyncio
async def test_task_assignees_unassign_unknown_sql_ko(client):
    owner = await create_user_and_auth(client, email="owner6_sql@example.com")
    resp = await client.post("/v1/tasks", headers=owner.headers, json={"label": "demo"})
    task_id = resp.json()["id"]

    random_user_id = str(uuid4())
    resp = await client.delete(
        f"/v1/tasks/{task_id}/assignees/{random_user_id}", headers=owner.headers
    )
    assert resp.status_code == HTTPStatus.NOT_FOUND
