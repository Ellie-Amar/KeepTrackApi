from __future__ import annotations

from uuid import UUID

import pytest
from fastapi import HTTPException

from app.domain.entities.user import User
from app.interfaces.security import get_current_user
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubTokenService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_ok():
    user = User.new(email="u@test.com", password_hash="hash")
    token_service = StubTokenService(payload={"sub": str(user.id)})
    repo = UserRepositoryInMemory()
    await repo.add(user)
    user_id = list(repo.users)[0].id  # ensure we use the stored UUID

    result = await get_current_user(
        token="any",
        token_service=StubTokenService(payload={"sub": str(user_id)}),
        user_repo=repo,
    )

    assert result == user


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_invalid_token_ko():
    token_service = StubTokenService(error=ValueError("invalid"))
    repo = UserRepositoryInMemory()

    with pytest.raises(HTTPException) as exc:
        await get_current_user(
            token="bad",
            token_service=token_service,
            user_repo=repo,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_missing_sub_ko():
    token_service = StubTokenService(payload={})
    repo = UserRepositoryInMemory()

    with pytest.raises(HTTPException) as exc:
        await get_current_user(
            token="bad",
            token_service=token_service,
            user_repo=repo,
        )

    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_current_user_user_not_found_ko():
    user = User.new(email="exists@test.com", password_hash="hash")
    token_service = StubTokenService(payload={"sub": str(user.id)})
    repo = UserRepositoryInMemory()

    with pytest.raises(HTTPException) as exc:
        await get_current_user(
            token="ok",
            token_service=token_service,
            user_repo=repo,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"
