from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.support.db import clear_users


@pytest_asyncio.fixture(autouse=True)
async def clean_users_table():
    await clear_users()


async def _create_user(client: AsyncClient, email: str, password: str) -> None:
    response = await client.post(
        "/v1/users",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_login_returns_token_ok(client: AsyncClient):
    email = "login-ok@example.com"
    password = "StrongPass123!"
    await _create_user(client, email, password)

    response = await client.post(
        "/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert "accessToken" in body
    assert body["tokenType"] == "bearer"


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_login_wrong_password_ko(client: AsyncClient):
    email = "login-wrong@example.com"
    await _create_user(client, email, "RightPassword123!")

    response = await client.post(
        "/v1/auth/token",
        data={"username": email, "password": "bad-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_login_unknown_user_ko(client: AsyncClient):
    response = await client.post(
        "/v1/auth/token",
        data={"username": "ghost@example.com", "password": "irrelevant"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401
