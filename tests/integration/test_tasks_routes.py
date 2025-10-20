from uuid import uuid4
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.interfaces.dependencies import get_task_repo
from app.infrastructure.repositories.in_memory.task_repository_in_memory import (
    TaskRepositoryInMemory,
)

@pytest.mark.integration
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
