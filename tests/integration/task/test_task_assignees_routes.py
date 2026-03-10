from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.application.usecases.task.assign_task_users_usecase import AssignTaskUsers
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.list_task_assignees_usecase import (
    ListTaskAssignees,
)
from app.application.usecases.task.remove_task_user_usecase import RemoveTaskUser
from app.interfaces.dependencies import (
    get_assign_task_users_uc,
    get_create_task_uc,
    get_list_task_assignees_uc,
    get_remove_task_user_uc,
    get_task_repo,
    get_user_repo,
)
from app.interfaces.security import get_current_user
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from app.main import app
from tests.integration.helpers.auth import make_set_current_user

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def override_repos():
    task_repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()

    async def _get_task_repo():
        return task_repo

    async def _get_user_repo():
        return user_repo

    async def _get_create_task_uc():
        return CreateTask(task_repo)

    async def _get_assign_task_users_uc():
        return AssignTaskUsers(task_repo, user_repo)

    async def _get_list_task_assignees_uc():
        return ListTaskAssignees(task_repo, user_repo)

    async def _get_remove_task_user_uc():
        return RemoveTaskUser(task_repo)

    app.dependency_overrides[get_task_repo] = _get_task_repo
    app.dependency_overrides[get_user_repo] = _get_user_repo
    app.dependency_overrides[get_create_task_uc] = _get_create_task_uc
    app.dependency_overrides[get_assign_task_users_uc] = _get_assign_task_users_uc
    app.dependency_overrides[get_list_task_assignees_uc] = _get_list_task_assignees_uc
    app.dependency_overrides[get_remove_task_user_uc] = _get_remove_task_user_uc
    yield task_repo, user_repo
    app.dependency_overrides.pop(get_task_repo, None)
    app.dependency_overrides.pop(get_user_repo, None)
    app.dependency_overrides.pop(get_create_task_uc, None)
    app.dependency_overrides.pop(get_assign_task_users_uc, None)
    app.dependency_overrides.pop(get_list_task_assignees_uc, None)
    app.dependency_overrides.pop(get_remove_task_user_uc, None)


@pytest.fixture
def set_current_user(override_repos):
    _, user_repo = override_repos
    helper = make_set_current_user(app)

    async def _use(user=None, *, email: str | None = None):
        selected = helper(user=user, email=email)
        await user_repo.add(selected)
        return selected

    yield _use
    app.dependency_overrides.pop(get_current_user, None)


async def _create_task(client: AsyncClient, label: str = "Task") -> str:
    response = await client.post("/v1/tasks", json={"label": label})
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.integration
async def test_task_assignees_assign_and_list_ok(set_current_user, client: AsyncClient):
    owner = await set_current_user(email="owner@example.com")
    task_id = await _create_task(client)

    assignee = await set_current_user(email="assignee@example.com")
    await set_current_user(owner)  # switch back to owner for assign
    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [assignee.email]},
    )
    assert resp.status_code == 201, resp.text

    resp = await client.get(f"/v1/tasks/{task_id}/assignees")
    assert resp.status_code == 200, resp.text
    emails = {u["email"] for u in resp.json()}
    assert emails == {owner.email, assignee.email}


@pytest.mark.integration
async def test_task_assignees_list_as_participant_ok(
    set_current_user, client: AsyncClient
):
    owner = await set_current_user(email="owner2@example.com")
    task_id = await _create_task(client)

    participant = await set_current_user(email="participant2@example.com")
    await set_current_user(owner)
    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [participant.email]},
    )
    assert resp.status_code == 201, resp.text

    await set_current_user(participant)
    resp = await client.get(f"/v1/tasks/{task_id}/assignees")
    assert resp.status_code == 200, resp.text
    emails = {u["email"] for u in resp.json()}
    assert participant.email in emails


@pytest.mark.integration
async def test_task_assignees_assign_missing_user_ko(
    set_current_user, client: AsyncClient
):
    await set_current_user(email="owner3@example.com")
    task_id = await _create_task(client)

    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": ["missing@example.com"]},
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.integration
async def test_task_assignees_assign_non_owner_ko(
    set_current_user, client: AsyncClient
):
    owner = await set_current_user(email="owner4@example.com")
    task_id = await _create_task(client)

    _participant = await set_current_user(email="participant4@example.com")
    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [owner.email]},
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.integration
async def test_task_assignees_unassign_ok(set_current_user, client: AsyncClient):
    owner = await set_current_user(email="owner5@example.com")
    task_id = await _create_task(client)

    assignee = await set_current_user(email="assignee5@example.com")
    await set_current_user(owner)
    resp = await client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [assignee.email]},
    )
    user_id = resp.json()[0]["id"]

    resp = await client.delete(f"/v1/tasks/{task_id}/assignees/{user_id}")
    assert resp.status_code == 204, resp.text

    resp = await client.get(f"/v1/tasks/{task_id}/assignees")
    emails = {u["email"] for u in resp.json()}
    assert assignee.email not in emails


@pytest.mark.integration
async def test_task_assignees_unassign_unknown_user_ko(
    set_current_user, client: AsyncClient
):
    await set_current_user(email="owner6@example.com")
    task_id = await _create_task(client)

    resp = await client.delete(
        f"/v1/tasks/{task_id}/assignees/{uuid4()}",
    )
    assert resp.status_code == 404, resp.text
