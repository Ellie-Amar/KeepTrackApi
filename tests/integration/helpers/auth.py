from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI
from httpx import AsyncClient

from app.domain.entities.user import User
from app.interfaces.security import get_current_user


@dataclass(slots=True)
class AuthContext:
    user: dict
    token: str
    refresh_token: str
    headers: dict[str, str]


async def create_user_and_auth(
    client: AsyncClient,
    *,
    email: str | None = None,
    password: str = "StrongPass123!",
    display_name: str | None = None,
) -> AuthContext:
    """Create a user via API then fetch a JWT token for subsequent calls."""
    resolved_email = email or f"user-{uuid4()}@example.com"

    user_payload: dict[str, str] = {
        "email": resolved_email,
        "password": password,
    }
    if display_name is not None:
        user_payload["displayName"] = display_name

    user_response = await client.post("/v1/users", json=user_payload)
    assert user_response.status_code == 201, user_response.text
    user_body = user_response.json()

    form_data = {
        "username": resolved_email,
        "password": password,
    }
    token_response = await client.post(
        "/v1/auth/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == 200, token_response.text
    token_body = token_response.json()

    headers = {"Authorization": f"Bearer {token_body['accessToken']}"}
    return AuthContext(
        user=user_body,
        token=token_body["accessToken"],
        refresh_token=token_body["refreshToken"],
        headers=headers,
    )


def make_set_current_user(app: FastAPI) -> Callable[..., User]:
    """Return a helper toggling the FastAPI dependency for get_current_user."""
    current: dict[str, User | None] = {"value": None}

    async def _override_get_current_user():
        if current["value"] is None:
            raise RuntimeError("call set_current_user() before hitting the API")
        return current["value"]

    app.dependency_overrides[get_current_user] = _override_get_current_user

    def use(
        user: User | None = None,
        *,
        email: str | None = None,
    ) -> User:
        selected = user or User.new(
            email=email or f"user-{uuid4()}@example.com",
            password_hash="hash",
        )
        current["value"] = selected
        return selected

    return use
