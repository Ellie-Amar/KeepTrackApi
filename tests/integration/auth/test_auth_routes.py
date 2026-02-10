from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.interfaces.dependencies import (
    get_password_hasher,
    get_token_service,
    get_user_repo,
)
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from app.main import app
from tests.support.stubs import StubHasher, StubTokenService


@pytest.fixture(autouse=True)
def override_auth_dependencies():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    token_service = StubTokenService()

    app.dependency_overrides[get_user_repo] = lambda: repo
    app.dependency_overrides[get_password_hasher] = lambda: hasher
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.state.test_token_service = token_service

    yield

    app.dependency_overrides.pop(get_user_repo, None)
    app.dependency_overrides.pop(get_password_hasher, None)
    app.dependency_overrides.pop(get_token_service, None)
    app.state.test_token_service = None


def _create_user(client: TestClient, email: str, password: str) -> None:
    response = client.post("/v1/users", json={"email": email, "password": password})
    assert response.status_code == 201, response.text


@pytest.mark.integration
def test_login_returns_token_ok():
    client = TestClient(app)
    email = "local-login@test.com"
    password = "StrongPass123!"
    _create_user(client, email, password)

    response = client.post(
        "/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "accessToken" in body
    assert "refreshToken" in body
    assert body["tokenType"] == "bearer"


@pytest.mark.integration
def test_login_wrong_password_ko():
    client = TestClient(app)
    email = "local-wrong@test.com"
    _create_user(client, email, "CorrectPass123!")

    response = client.post(
        "/v1/auth/token",
        data={"username": email, "password": "bad-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_refresh_returns_new_tokens_ok():
    client = TestClient(app)
    email = "refresh-ok@test.com"
    password = "StrongPass123!"
    _create_user(client, email, password)

    login_response = client.post(
        "/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200, login_response.text
    login_body = login_response.json()

    # Configure stub payload to validate refresh token
    user_id = login_body["accessToken"].split("::")[-1]
    app.state.test_token_service.payload = {"sub": user_id}

    response = client.post(
        "/v1/auth/refresh",
        json={"refreshToken": login_body["refreshToken"]},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "accessToken" in body
    assert "refreshToken" in body
    assert body["tokenType"] == "bearer"


@pytest.mark.integration
def test_refresh_invalid_token_ko():
    client = TestClient(app)
    email = "refresh-ko@test.com"
    password = "StrongPass123!"
    _create_user(client, email, password)

    login_response = client.post(
        "/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200, login_response.text

    app.state.test_token_service.error = ValueError("bad token")

    response = client.post(
        "/v1/auth/refresh",
        json={"refreshToken": "invalid"},
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_login_unknown_user_ko():
    client = TestClient(app)

    response = client.post(
        "/v1/auth/token",
        data={"username": "ghost@test.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
