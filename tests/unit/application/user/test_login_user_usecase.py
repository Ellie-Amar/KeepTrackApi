from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.application.commands.login_user_command import LoginUserCommand
from app.application.usecases.auth.login_user_usecase import LoginUserUseCase
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from app.domain.entities.user import User
from tests.support.stubs import StubHasher, StubTokenService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_ok():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    tokens = StubTokenService()
    uc = LoginUserUseCase(repo, hasher, tokens)

    password = "StrongPass123"
    stored = User.new(
        email="user@example.com",
        password_hash=hasher.hash(password),
    )
    await repo.add(stored)

    token = await uc.execute(
        LoginUserCommand(email="user@example.com", password=password)
    )

    assert token.startswith("token::")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_unknown_email_ko():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    tokens = StubTokenService()
    uc = LoginUserUseCase(repo, hasher, tokens)

    with pytest.raises(HTTPException) as exc:
        await uc.execute(LoginUserCommand(email="ghost@example.com", password="pass"))

    assert exc.value.status_code == 401


@pytest.mark.unit
@pytest.mark.asyncio
async def test_login_user_wrong_password_ko():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    tokens = StubTokenService()
    uc = LoginUserUseCase(repo, hasher, tokens)

    stored = User.new(
        email="user@example.com",
        password_hash=hasher.hash("correct-pass"),
    )
    await repo.add(stored)

    with pytest.raises(HTTPException) as exc:
        await uc.execute(
            LoginUserCommand(email="user@example.com", password="wrong-pass")
        )

    assert exc.value.status_code == 401
