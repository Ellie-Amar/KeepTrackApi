from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.interfaces.dependencies import get_task_repo, get_user_repo
from app.interfaces.security import get_current_user
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from app.main import app
from tests.integration.helpers.auth import make_set_current_user


@pytest.fixture(autouse=True)
def override_repos():
    task_repo = TaskRepositoryInMemory()
    user_repo = UserRepositoryInMemory()
    app.dependency_overrides[get_task_repo] = lambda: task_repo
    app.dependency_overrides[get_user_repo] = lambda: user_repo
    yield task_repo, user_repo
    app.dependency_overrides.pop(get_task_repo, None)
    app.dependency_overrides.pop(get_user_repo, None)


@pytest.fixture
def set_current_user(override_repos):
    _, user_repo = override_repos
    helper = make_set_current_user(app)

    def _use(user=None, *, email: str | None = None):
        selected = helper(user=user, email=email)
        # UserRepositoryInMemory is sync-safe here
        # but keep API consistent with repo interface
        # by calling add through loop
        import asyncio

        asyncio.get_event_loop().run_until_complete(user_repo.add(selected))
        return selected

    yield _use
    app.dependency_overrides.pop(get_current_user, None)


def _create_task(client: TestClient, label: str = "Task") -> str:
    response = client.post("/v1/tasks", json={"label": label})
    assert response.status_code == 201, response.text
    return response.json()["id"]


@pytest.mark.integration
def test_task_assignees_assign_and_list_ok(set_current_user):
    owner = set_current_user(email="owner@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    assignee = set_current_user(email="assignee@example.com")
    set_current_user(owner)  # switch back to owner for assign
    resp = client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [assignee.email]},
    )
    assert resp.status_code == 201, resp.text

    resp = client.get(f"/v1/tasks/{task_id}/assignees")
    assert resp.status_code == 200, resp.text
    emails = {u["email"] for u in resp.json()}
    assert emails == {owner.email, assignee.email}


@pytest.mark.integration
def test_task_assignees_list_as_participant_ok(set_current_user):
    owner = set_current_user(email="owner2@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    participant = set_current_user(email="participant2@example.com")
    set_current_user(owner)
    resp = client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [participant.email]},
    )
    assert resp.status_code == 201, resp.text

    set_current_user(participant)
    resp = client.get(f"/v1/tasks/{task_id}/assignees")
    assert resp.status_code == 200, resp.text
    emails = {u["email"] for u in resp.json()}
    assert participant.email in emails


@pytest.mark.integration
def test_task_assignees_assign_missing_user_ko(set_current_user):
    set_current_user(email="owner3@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    resp = client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": ["missing@example.com"]},
    )
    assert resp.status_code == 400, resp.text


@pytest.mark.integration
def test_task_assignees_assign_non_owner_ko(set_current_user):
    owner = set_current_user(email="owner4@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    _participant = set_current_user(email="participant4@example.com")
    resp = client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [owner.email]},
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.integration
def test_task_assignees_unassign_ok(set_current_user):
    owner = set_current_user(email="owner5@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    assignee = set_current_user(email="assignee5@example.com")
    set_current_user(owner)
    resp = client.post(
        f"/v1/tasks/{task_id}/assignees",
        json={"userEmails": [assignee.email]},
    )
    user_id = resp.json()[0]["id"]

    resp = client.delete(f"/v1/tasks/{task_id}/assignees/{user_id}")
    assert resp.status_code == 204, resp.text

    resp = client.get(f"/v1/tasks/{task_id}/assignees")
    emails = {u["email"] for u in resp.json()}
    assert assignee.email not in emails


@pytest.mark.integration
def test_task_assignees_unassign_unknown_user_ko(set_current_user):
    set_current_user(email="owner6@example.com")
    client = TestClient(app)
    task_id = _create_task(client)

    resp = client.delete(
        f"/v1/tasks/{task_id}/assignees/{uuid4()}",
    )
    assert resp.status_code == 404, resp.text
