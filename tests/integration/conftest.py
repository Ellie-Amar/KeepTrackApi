from __future__ import annotations

from collections.abc import Awaitable, Callable

import pytest_asyncio
from httpx import AsyncClient

from tests.integration.helpers.auth import AuthContext, create_user_and_auth


AuthFactory = Callable[..., Awaitable[AuthContext]]


@pytest_asyncio.fixture
def auth_factory(client: AsyncClient) -> AuthFactory:
    async def _factory(**kwargs) -> AuthContext:
        return await create_user_and_auth(client, **kwargs)

    return _factory
