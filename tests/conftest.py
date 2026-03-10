from __future__ import annotations
from typing import AsyncIterator
from dataclasses import dataclass
import os

# Activate NullPool for SQLAlchemy during tests (prevents cross-loop issues)
os.environ.setdefault("SQLA_NULLPOOL", "1")

import pytest_asyncio
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient, ASGITransport
from app.main import app


@dataclass(slots=True)
class _PasswordForm:
    username: str
    password: str


@pytest_asyncio.fixture(autouse=True)
async def override_oauth2_password_form():
    async def _get_form(request: Request) -> _PasswordForm:
        form = await request.form()
        return _PasswordForm(
            username=form.get("username", ""),
            password=form.get("password", ""),
        )

    app.dependency_overrides[OAuth2PasswordRequestForm] = _get_form
    yield
    app.dependency_overrides.pop(OAuth2PasswordRequestForm, None)


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client sharing the same event loop as the tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
