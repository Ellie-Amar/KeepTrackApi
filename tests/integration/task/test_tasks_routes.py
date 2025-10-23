from uuid import uuid4
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.interfaces.dependencies import get_task_repo
from app.infrastructure.repositories.in_memory.task_repository_in_memory import (
    TaskRepositoryInMemory,
)


@pytest.fixture(autouse=True)
def override_repo():
    """Override the task repository with an in-memory implementation for each test."""
    repo = TaskRepositoryInMemory()
    app.dependency_overrides[get_task_repo] = lambda: repo
    yield
    app.dependency_overrides.clear()


@pytest.mark.integration
def test_list_tasks_empty_ok():
    """List endpoint should return an empty list when no tasks exist."""
    client = TestClient(app)
    response = client.get("/v1/tasks")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.integration
def test_create_then_list_tasks_ok():
    """After creating a task, it should appear in the list endpoint."""
    client = TestClient(app)
    payload = {
        "userId": str(uuid4()),  # camelCase supported via alias generator
        "label": "Drink water",
        "note": "500ml",
        "category": "health",
    }

    # Create
    response = client.post("/v1/tasks", json=payload)
    assert response.status_code == 201, response.text
    created = response.json()
    assert created["label"] == "Drink water"
    assert "id" in created

    # List
    response = client.get("/v1/tasks")
    assert response.status_code == 200
    items = response.json()
    assert any(it["id"] == created["id"] for it in items)


@pytest.mark.integration
def test_create_task_validation_ko():
    """Should return 422 when label is empty."""
    client = TestClient(app)
    payload = {
        "userId": str(uuid4()),
        "label": "",  # invalid (min_length=1)
    }
    response = client.post("/v1/tasks", json=payload)

    assert response.status_code == 422


@pytest.mark.integration
def test_get_task_by_id_ok():
    """After creating a task, GET by id should return 200 with the same task."""
    client = TestClient(app)
    payload = {
        "userId": str(uuid4()),
        "label": "Read book",
        "note": "Chapter 1",
        "category": "personal",
    }
    r_create = client.post("/v1/tasks", json=payload)
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_get = client.get(f"/v1/tasks/{created['id']}")
    assert r_get.status_code == 200
    body = r_get.json()
    assert body["id"] == created["id"]
    assert body["label"] == "Read book"
    # CamelCase
    assert "createdAt" in body and "updatedAt" in body


@pytest.mark.integration
def test_get_task_by_id_not_found_ko():
    """GET by id should return 404 for unknown id."""
    client = TestClient(app)
    r = client.get(f"/v1/tasks/{uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


@pytest.mark.integration
def test_patch_task_partial_update_ok():
    """PATCH should update only provided fields and return 200."""
    client = TestClient(app)
    r_create = client.post(
        "/v1/tasks", json={"userId": str(uuid4()), "label": "Before"}
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = client.patch(
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
def test_patch_task_not_found_ko():
    """PATCH unknown id should return 404."""
    client = TestClient(app)
    r = client.patch(f"/v1/tasks/{uuid4()}", json={"label": "Nope"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


@pytest.mark.integration
def test_patch_task_validation_label_empty_ko():
    """PATCH with label='' should return 422 (min_length=1 on TaskUpdate)."""
    client = TestClient(app)
    # Create a valid task first
    r_create = client.post("/v1/tasks", json={"userId": str(uuid4()), "label": "Ok"})
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_patch = client.patch(f"/v1/tasks/{created['id']}", json={"label": ""})
    assert r_patch.status_code == 422, r_patch.text


@pytest.mark.integration
def test_delete_task_ok_then_not_found_ko():
    """DELETE should return 204 once, then 404 if called again (semantics A)."""
    client = TestClient(app)
    r_create = client.post(
        "/v1/tasks", json={"userId": str(uuid4()), "label": "ToDelete"}
    )
    assert r_create.status_code == 201, r_create.text
    created = r_create.json()

    r_del1 = client.delete(f"/v1/tasks/{created['id']}")
    assert r_del1.status_code == 204, r_del1.text

    r_del2 = client.delete(f"/v1/tasks/{created['id']}")
    assert r_del2.status_code == 404
    assert r_del2.json()["detail"] == "Task not found"
