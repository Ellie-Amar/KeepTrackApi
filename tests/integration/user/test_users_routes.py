from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from app.interfaces.dependencies import get_create_user_uc, get_verify_user_email_uc
from app.application.usecases.user.create_user_usecase import CreateUser
from app.application.usecases.user.verify_user_email_usecase import VerifyUserEmail
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubEmailSender, StubHasher, StubTokenService

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def override_user_repo():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    token_service = StubTokenService()
    email_sender = StubEmailSender()

    async def _get_create_user_uc():
        return CreateUser(
            repo,
            hasher,
            token_service,
            email_sender,
            "http://localhost:8000/v1/users/verify-email",
        )

    async def _get_verify_user_email_uc():
        return VerifyUserEmail(repo, token_service)

    app.dependency_overrides[get_create_user_uc] = _get_create_user_uc
    app.dependency_overrides[get_verify_user_email_uc] = _get_verify_user_email_uc
    app.state.test_user_repo = repo
    app.state.test_token_service = token_service
    yield
    app.dependency_overrides.pop(get_create_user_uc, None)
    app.dependency_overrides.pop(get_verify_user_email_uc, None)
    app.state.test_user_repo = None
    app.state.test_token_service = None


@pytest.mark.integration
async def test_create_user_ok(client: AsyncClient):
    response = await client.post(
        "/v1/users",
        json={
            "email": "local@test.com",
            "password": "StrongPass123",
            "displayName": "Local",
        },
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "local@test.com"
    assert body["displayName"] == "Local"
    assert body["isActive"] is True
    assert "id" in body


@pytest.mark.integration
async def test_create_user_duplicate_email_ko(client: AsyncClient):
    first = await client.post(
        "/v1/users", json={"email": "dup@test.com", "password": "StrongPass123"}
    )
    assert first.status_code == 201, first.text

    dup = await client.post(
        "/v1/users", json={"email": "Dup@Test.com", "password": "StrongPass123"}
    )
    assert dup.status_code == 400, dup.text


@pytest.mark.integration
async def test_create_user_weak_password_ko(client: AsyncClient):
    response = await client.post(
        "/v1/users", json={"email": "weak@test.com", "password": "short"}
    )

    assert response.status_code == 422, response.text


@pytest.mark.integration
async def test_verify_user_email_ok(client: AsyncClient):
    create = await client.post(
        "/v1/users",
        json={"email": "verify@test.com", "password": "StrongPass123"},
    )
    assert create.status_code == 201, create.text
    body = create.json()
    token_service = app.state.test_token_service
    assert token_service is not None
    token_service.payload = {"sub": body["id"], "email": body["email"]}

    verify = await client.get("/v1/users/verify-email", params={"token": "fake-token"})
    assert verify.status_code == 200, verify.text
    verify_body = verify.json()
    assert verify_body["emailVerified"] is True
