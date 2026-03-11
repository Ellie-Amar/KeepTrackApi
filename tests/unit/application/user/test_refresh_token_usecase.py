from __future__ import annotations

import pytest

from app.application.commands.refresh_token_command import RefreshTokenCommand
from app.application.errors import AuthUserNotFoundError, InvalidTokenError
from app.application.usecases.auth.refresh_token_usecase import RefreshTokenUseCase
from app.domain.entities.user import User
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubTokenService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_token_usecase_ok():
    repo = UserRepositoryInMemory()
    user = User.new(email="refresh-ok@test.com", password_hash="hash")
    await repo.add(user)

    token_service = StubTokenService(payload={"sub": str(user.id)})
    uc = RefreshTokenUseCase(token_service, repo)

    tokens = await uc.execute(RefreshTokenCommand(refresh_token="refresh-token"))

    assert tokens.access_token.startswith("token::")
    assert tokens.refresh_token.startswith("refresh::")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_token_usecase_invalid_token_ko():
    repo = UserRepositoryInMemory()
    token_service = StubTokenService(error=ValueError("invalid token"))
    uc = RefreshTokenUseCase(token_service, repo)

    with pytest.raises(InvalidTokenError) as exc:
        await uc.execute(RefreshTokenCommand(refresh_token="bad-token"))

    assert str(exc.value) == "Invalid or expired token"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_refresh_token_usecase_user_not_found_ko():
    repo = UserRepositoryInMemory()
    missing_user_id = User.new(email="missing@test.com", password_hash="hash").id
    token_service = StubTokenService(payload={"sub": str(missing_user_id)})
    uc = RefreshTokenUseCase(token_service, repo)

    with pytest.raises(AuthUserNotFoundError) as exc:
        await uc.execute(RefreshTokenCommand(refresh_token="refresh-token"))

    assert str(exc.value) == "User not found"
