from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient

from tests.support.db import clear_users


@pytest_asyncio.fixture(autouse=True)
async def clean_users_table():
    await clear_users()


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_user_ok(client: AsyncClient):
    r = await client.post(
        "/v1/users",
        json={"email": "u@ex.com", "password": "strongpass", "displayName": "U"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == "u@ex.com"
    assert body["isActive"] is True
    assert "id" in body


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_user_duplicate_email_ko(client: AsyncClient):
    # first
    r1 = await client.post(
        "/v1/users", json={"email": "ski@bi.di", "password": "strongpass"}
    )
    assert r1.status_code == 201, r1.text
    # duplicate (case-insensitive)
    r2 = await client.post(
        "/v1/users", json={"email": "SKi@Bi.Di", "password": "strongpass"}
    )
    assert r2.status_code == 400, r2.text


@pytest.mark.sql
@pytest.mark.asyncio
async def test_sql_create_user_weak_password_ko(client: AsyncClient):
    # first
    r1 = await client.post("/v1/users", json={"email": "ski@bi.di", "password": "i"})
    assert r1.status_code == 422, r1.text
