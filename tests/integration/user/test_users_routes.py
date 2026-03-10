from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.main import app
from app.interfaces.dependencies import get_create_user_uc
from app.application.usecases.user.create_user_usecase import CreateUser
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubHasher

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def override_user_repo():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()

    async def _get_create_user_uc():
        return CreateUser(repo, hasher)

    app.dependency_overrides[get_create_user_uc] = _get_create_user_uc
    yield
    app.dependency_overrides.pop(get_create_user_uc, None)


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
