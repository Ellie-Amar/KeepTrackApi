from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.entities.user import User
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)
from app.interfaces.dependencies import get_task_repo, get_task_validation_repo
from app.interfaces.security import get_current_user
from app.main import app
from tests.integration.helpers.auth import make_set_current_user


@pytest.fixture(autouse=True)
def override_repositories():
    validation_repo = TaskValidationRepositoryInMemory()
    task_repo = TaskRepositoryInMemory(validation_repo=validation_repo)
    app.dependency_overrides[get_task_repo] = lambda: task_repo
    app.dependency_overrides[get_task_validation_repo] = lambda: validation_repo
    yield
    app.dependency_overrides.pop(get_task_repo, None)
    app.dependency_overrides.pop(get_task_validation_repo, None)


@pytest.fixture
def set_current_user():
    helper = make_set_current_user(app)
    yield helper
    app.dependency_overrides.pop(get_current_user, None)


def _create_task(client: TestClient) -> str:
    response = client.post("/v1/tasks", json={"label": "Daily task"})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def _make_user_with_name(name: str | None) -> User:
    return User.new(
        email=f"user-{uuid4()}@example.com",
        password_hash="hash",
        display_name=name,
    )


@pytest.mark.integration
def test_create_task_validation_returns_user_info_ok(set_current_user):
    user = _make_user_with_name("Tester Name")
    set_current_user(user=user)
    client = TestClient(app)
    task_id = _create_task(client)

    response = client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "Done"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["note"] == "Done"
    assert body["user"]["id"] == str(user.id)
    assert body["user"]["displayName"] == "Tester Name"


@pytest.mark.integration
def test_patch_task_validation_updates_note_ok(set_current_user):
    set_current_user(user=_make_user_with_name("Tester"))
    client = TestClient(app)
    task_id = _create_task(client)
    created = client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "old"},
    ).json()

    response = client.patch(
        f"/v1/tasks/{task_id}/validations/{created['id']}",
        json={"note": "updated"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["note"] == "updated"


@pytest.mark.integration
def test_delete_task_validation_removes_from_list_ok(set_current_user):
    set_current_user(user=_make_user_with_name(None))
    client = TestClient(app)
    task_id = _create_task(client)
    created = client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "temp"},
    ).json()

    delete_response = client.delete(
        f"/v1/tasks/{task_id}/validations/{created['id']}",
    )
    assert delete_response.status_code == 204, delete_response.text

    list_response = client.get("/v1/tasks")
    assert list_response.status_code == 200
    tasks = list_response.json()
    assert len(tasks[0]["validations"]) == 0


@pytest.mark.integration
def test_list_tasks_includes_validations_with_user_ok(set_current_user):
    user = _make_user_with_name("Valider")
    set_current_user(user=user)
    client = TestClient(app)
    task_id = _create_task(client)
    client.post(f"/v1/tasks/{task_id}/validations", json={"note": "first"})

    response = client.get("/v1/tasks")

    assert response.status_code == 200
    items = response.json()
    assert len(items[0]["validations"]) == 1
    validation = items[0]["validations"][0]
    assert validation["note"] == "first"
    assert validation["user"]["id"] == str(user.id)
    assert validation["user"]["displayName"] == "Valider"


@pytest.mark.integration
def test_patch_task_validation_other_user_ko(set_current_user):
    first_user = _make_user_with_name("Owner")
    second_user = _make_user_with_name("Intruder")
    set_current_user(user=first_user)
    client = TestClient(app)
    task_id = _create_task(client)
    created = client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "protected"},
    ).json()

    set_current_user(user=second_user)
    response = client.patch(
        f"/v1/tasks/{task_id}/validations/{created['id']}",
        json={"note": "hack"},
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_delete_task_validation_other_user_ko(set_current_user):
    first_user = _make_user_with_name("Owner")
    second_user = _make_user_with_name("Intruder")
    set_current_user(user=first_user)
    client = TestClient(app)
    task_id = _create_task(client)
    created = client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": "protected"},
    ).json()

    set_current_user(user=second_user)
    response = client.delete(
        f"/v1/tasks/{task_id}/validations/{created['id']}",
    )

    assert response.status_code == 404
