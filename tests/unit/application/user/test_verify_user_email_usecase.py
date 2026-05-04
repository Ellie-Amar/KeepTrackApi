from __future__ import annotations

import pytest

from app.application.errors import AuthUserNotFoundError, InvalidTokenError
from app.application.usecases.user.verify_user_email_usecase import VerifyUserEmail
from app.domain.entities.user import User
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubTokenService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_user_email_ok():
    repo = UserRepositoryInMemory()
    user = User.new(
        email="user@example.com", password_hash="hash", email_verified=False
    )
    await repo.add(user)
    token_service = StubTokenService(payload={"sub": str(user.id), "email": user.email})
    uc = VerifyUserEmail(repo, token_service)

    verified = await uc.execute("token")

    assert verified.email_verified is True
    saved = await repo.get_by_id(user.id)
    assert saved is not None
    assert saved.email_verified is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_user_email_invalid_token_ko():
    repo = UserRepositoryInMemory()
    token_service = StubTokenService(error=ValueError("bad token"))
    uc = VerifyUserEmail(repo, token_service)

    with pytest.raises(InvalidTokenError):
        await uc.execute("bad")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verify_user_email_missing_user_ko():
    repo = UserRepositoryInMemory()
    token_service = StubTokenService(
        payload={
            "sub": "f0d74c11-d4e0-4dde-8fd4-8f3550f9fe28",
            "email": "ghost@example.com",
        }
    )
    uc = VerifyUserEmail(repo, token_service)

    with pytest.raises(AuthUserNotFoundError):
        await uc.execute("token")
