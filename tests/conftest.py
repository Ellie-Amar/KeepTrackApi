from __future__ import annotations
from typing import AsyncIterator
from dataclasses import dataclass
import os
import socket
from urllib.parse import urlparse

# Activate NullPool for SQLAlchemy during tests (prevents cross-loop issues)
os.environ.setdefault("SQLA_NULLPOOL", "1")
# Ensure test-specific dependency behavior is enabled during pytest runs.
os.environ.setdefault("APP_ENV", "test")

import pytest
import pytest_asyncio
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient, ASGITransport
from app.config.settings import settings
from app.main import app

_SQL_REACHABLE: tuple[bool, str] | None = None
_SQL_REQUIRED = os.getenv("SQL_TESTS_REQUIRED") == "1"


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


def _probe_sql_reachability() -> tuple[bool, str]:
    if not settings.database_url:
        return False, "DATABASE_URL is not set"

    parsed = urlparse(settings.database_url)
    if parsed.hostname is None:
        return False, "DATABASE_URL host is missing"

    port = parsed.port or 5432
    try:
        with socket.create_connection((parsed.hostname, port), timeout=0.5):
            return True, ""
    except OSError as exc:
        return False, f"Cannot reach PostgreSQL at {parsed.hostname}:{port} ({exc})"


def pytest_runtest_setup(item: pytest.Item) -> None:
    if item.get_closest_marker("sql") is None:
        return

    global _SQL_REACHABLE
    if _SQL_REACHABLE is None:
        _SQL_REACHABLE = _probe_sql_reachability()

    reachable, reason = _SQL_REACHABLE
    if not reachable:
        if _SQL_REQUIRED:
            raise RuntimeError(
                f"SQL tests required but database is unavailable: {reason}"
            )
        pytest.skip(f"SQL tests skipped: {reason}")


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client sharing the same event loop as the tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
