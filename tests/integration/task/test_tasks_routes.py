from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.delete_task_usecase import DeleteTask
from app.application.usecases.task.list_tasks_with_validations_usecase import (
    ListTasksWithValidations,
)
from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.domain.entities.user import User
from app.interfaces.dependencies import (
    get_create_task_uc,
    get_create_task_validation_uc,
    get_delete_task_uc,
    get_list_tasks_with_validations_uc,
    get_task_repo,
    get_task_validation_repo,
    get_update_task_uc,
)
from app.interfaces.security import get_current_user
from app.main import app
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)
from tests.integration.helpers.auth import make_set_current_user

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def override_repo():
    """Override the task repository with an in-memory implementation for each test."""
    validation_repo = TaskValidationRepositoryInMemory()
    repo = TaskRepositoryInMemory(validation_repo=validation_repo)

    async def _get_task_repo():
        return repo

    async def _get_task_validation_repo():
        return validation_repo

    async def _get_create_task_uc():
        return CreateTask(repo)

    async def _get_list_tasks_with_validations_uc():
        return ListTasksWithValidations(repo)

    async def _get_update_task_uc():
        return UpdateTask(repo)

    async def _get_delete_task_uc():
        return DeleteTask(repo)

    async def _get_create_task_validation_uc():
        return CreateTaskValidation(validation_repo)

    app.dependency_overrides[get_task_repo] = _get_task_repo
    app.dependency_overrides[get_task_validation_repo] = _get_task_validation_repo
    app.dependency_overrides[get_create_task_uc] = _get_create_task_uc
    app.dependency_overrides[get_list_tasks_with_validations_uc] = (
        _get_list_tasks_with_validations_uc
    )
    app.dependency_overrides[get_update_task_uc] = _get_update_task_uc
    app.dependency_overrides[get_delete_task_uc] = _get_delete_task_uc
    app.dependency_overrides[get_create_task_validation_uc] = (
        _get_create_task_validation_uc
    )
    yield
    app.dependency_overrides.pop(get_task_repo, None)
    app.dependency_overrides.pop(get_task_validation_repo, None)
    app.dependency_overrides.pop(get_create_task_uc, None)
    app.dependency_overrides.pop(get_list_tasks_with_validations_uc, None)
    app.dependency_overrides.pop(get_update_task_uc, None)
    app.dependency_overrides.pop(get_delete_task_uc, None)
    app.dependency_overrides.pop(get_create_task_validation_uc, None)


@pytest.fixture
def set_current_user():
    helper = make_set_current_user(app)
    yield helper
    app.dependency_overrides.pop(get_current_user, None)


async def _create_task(client: AsyncClient, label: str = "Task") -> str:
    response = await client.post("/v1/tasks", json={"label": label})
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _create_validation(
    client: AsyncClient, task_id: str, note: str = "note"
) -> dict:
    response = await client.post(
        f"/v1/tasks/{task_id}/validations",
        json={"note": note},
    )
    assert response.status_code == 201, response.text
    return response.json()


def _user_with_name(name: str | None) -> User:
    return User.new(
        email=f"user-{uuid4()}@example.com",
        password_hash="hash",
        display_name=name,
    )


@pytest.mark.integration
async def test_list_tasks_empty_ok(set_current_user, client: AsyncClient):
    """List endpoint should return an empty list when no tasks exist."""
    set_current_user()
    response = await client.get("/v1/tasks")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
async def test_create_then_list_tasks_ok(set_current_user, client: AsyncClient):
    """After creating a task, it should appear in the list endpoint."""
    user = set_current_user(email="owner@example.test")
    payload = {
        "label": "Drink water",
        "note": "500ml",
        "category": "health",
    }

    # Create
    response = await client.post("/v1/tasks", json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["label"] == "Drink water"
    assert created["ownerId"] == str(user.id)
    assert "id" in created

    # List
    response = await client.get("/v1/tasks")
    assert response.status_code == 200
    items = response.json()
    assert any(it["id"] == created["id"] for it in items)


@pytest.mark.integration
async def test_list_tasks_includes_validations_ok(
    set_current_user, client: AsyncClient
):
    set_current_user(user=_user_with_name("Owner"))
    task_id = await _create_task(client)
    await _create_validation(client, task_id, note="done")

    response = await client.get("/v1/tasks")

    assert response.status_code == 200, response.text
    items = response.json()
    assert len(items[0]["validations"]) == 1
    assert items[0]["validations"][0]["note"] == "done"


@pytest.mark.integration
async def test_list_tasks_validations_hidden_for_other_user_ko(
    set_current_user, client: AsyncClient
):
    set_current_user(email="owner@example.test")
    task_id = await _create_task(client)
    await _create_validation(client, task_id, note="owner only")

    set_current_user(email="other@example.test")
    response = await client.get("/v1/tasks")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
async def test_create_task_validation_ko(set_current_user, client: AsyncClient):
    """Should return 422 when label is empty."""
    set_current_user()
    payload = {
        "label": "",  # invalid (min_length=1)
    }
    response = await client.post("/v1/tasks", json=payload)

    assert response.status_code == 422


@pytest.mark.integration
async def test_get_task_by_id_ok(set_current_user, client: AsyncClient):
    """After creating a task, GET by id should return 200 with the same task."""
    set_current_user()
    payload = {
        "label": "Read book",
        "note": "Chapter 1",
        "category": "personal",
    }
    r_create = await client.post("/v1/tasks", json=payload)
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_get = await client.get(f"/v1/tasks/{created['id']}")
    assert r_get.status_code == 200
    body = r_get.json()
    assert body["id"] == created["id"]
    assert body["label"] == "Read book"
    # CamelCase
    assert "createdAt" in body and "updatedAt" in body


@pytest.mark.integration
async def test_get_task_includes_validations_ok(set_current_user, client: AsyncClient):
    set_current_user(user=_user_with_name("Owner"))
    task_id = await _create_task(client)
    await _create_validation(client, task_id, note="first")

    response = await client.get(f"/v1/tasks/{task_id}")

    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["validations"]) == 1
    assert body["validations"][0]["note"] == "first"


@pytest.mark.integration
async def test_get_task_validations_other_user_ko(
    set_current_user, client: AsyncClient
):
    set_current_user(email="owner@example.test")
    task_id = await _create_task(client)
    await _create_validation(client, task_id, note="first")

    set_current_user(email="other@example.test")
    response = await client.get(f"/v1/tasks/{task_id}")

    assert response.status_code == 404


@pytest.mark.integration
async def test_get_task_by_id_not_found_ko(set_current_user, client: AsyncClient):
    """GET by id should return 404 for unknown id."""
    set_current_user()
    r = await client.get(f"/v1/tasks/{uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


@pytest.mark.integration
async def test_patch_task_partial_update_ok(set_current_user, client: AsyncClient):
    """PATCH should update only provided fields and return 200."""
    set_current_user()
    r_create = await client.post("/v1/tasks", json={"label": "Before"})
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
    # updatedAt should change
    assert body["updatedAt"] != created["updatedAt"]


@pytest.mark.integration
async def test_patch_task_not_found_ko(set_current_user, client: AsyncClient):
    """PATCH unknown id should return 404."""
    set_current_user()
    r = await client.patch(f"/v1/tasks/{uuid4()}", json={"label": "Nope"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


@pytest.mark.integration
async def test_patch_task_validation_label_empty_ko(
    set_current_user, client: AsyncClient
):
    """PATCH with label='' should return 422 (min_length=1 on TaskUpdate)."""
    set_current_user()
    # Create a valid task first
    r_create = await client.post("/v1/tasks", json={"label": "Ok"})
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = await client.patch(f"/v1/tasks/{created['id']}", json={"label": ""})
    assert r_patch.status_code == 422, r_patch.text


@pytest.mark.integration
async def test_delete_task_ok_then_not_found_ko(set_current_user, client: AsyncClient):
    """DELETE should return 204 once, then 404 if called again (semantics A)."""
    set_current_user()
    r_create = await client.post("/v1/tasks", json={"label": "ToDelete"})
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_del1 = await client.delete(f"/v1/tasks/{created['id']}")
    assert r_del1.status_code == 204, r_del1.text

    r_del2 = await client.delete(f"/v1/tasks/{created['id']}")
    assert r_del2.status_code == 404
    assert r_del2.json()["detail"] == "Task not found"


@pytest.mark.integration
async def test_list_tasks_is_scoped_to_authenticated_user(
    set_current_user, client: AsyncClient
):
    """Ensure each user only sees their own tasks in-memory as well."""
    set_current_user(email="owner@example.test")
    await client.post("/v1/tasks", json={"label": "Owner task"})

    other = set_current_user(email="other@example.test")
    await client.post("/v1/tasks", json={"label": "Other task"})

    response = await client.get("/v1/tasks")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["label"] == "Other task"
    assert items[0]["ownerId"] == str(other.id)


@pytest.mark.integration
async def test_task_access_denied_for_other_user(set_current_user, client: AsyncClient):
    """GET/PATCH/DELETE must return 404 for a different authenticated user."""
    _ = set_current_user(email="owner-access@example.test")
    create_resp = await client.post("/v1/tasks", json={"label": "Owner secret"})
    assert create_resp.status_code == 201, create_resp.text
    task_id = create_resp.json()["id"]

    set_current_user(email="intruder@example.test")

    resp_get = await client.get(f"/v1/tasks/{task_id}")
    assert resp_get.status_code == 404

    resp_patch = await client.patch(
        f"/v1/tasks/{task_id}", json={"label": "Hack attempt"}
    )
    assert resp_patch.status_code == 404

    resp_delete = await client.delete(f"/v1/tasks/{task_id}")
    assert resp_delete.status_code == 404
