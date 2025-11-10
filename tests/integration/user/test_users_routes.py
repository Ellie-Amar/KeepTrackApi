from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.interfaces.dependencies import get_user_repo
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)


@pytest.fixture(autouse=True)
def override_user_repo():
    repo = UserRepositoryInMemory()
    app.dependency_overrides[get_user_repo] = lambda: repo
    yield
    app.dependency_overrides.pop(get_user_repo, None)


@pytest.mark.integration
def test_create_user_ok():
    client = TestClient(app)
    response = client.post(
        "/v1/users",
        json={"email": "local@test.com", "password": "StrongPass123", "displayName": "Local"},
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "local@test.com"
    assert body["displayName"] == "Local"
    assert body["isActive"] is True
    assert "id" in body


@pytest.mark.integration
def test_create_user_duplicate_email_ko():
    client = TestClient(app)

    first = client.post(
        "/v1/users", json={"email": "dup@test.com", "password": "StrongPass123"}
    )
    assert first.status_code == 201, first.text

    dup = client.post(
        "/v1/users", json={"email": "Dup@Test.com", "password": "StrongPass123"}
    )
    assert dup.status_code == 400, dup.text


@pytest.mark.integration
def test_create_user_weak_password_ko():
    client = TestClient(app)

    response = client.post(
        "/v1/users", json={"email": "weak@test.com", "password": "short"}
    )

    assert response.status_code == 422, response.text
