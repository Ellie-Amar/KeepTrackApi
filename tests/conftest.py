from __future__ import annotations
from typing import AsyncIterator
import os

# Activate NullPool for SQLAlchemy during tests (prevents cross-loop issues)
os.environ.setdefault("SQLA_NULLPOOL", "1")

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """HTTP client sharing the same event loop as the tests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
        
