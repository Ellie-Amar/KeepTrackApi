from __future__ import annotations

import pytest

from app.application.usecases.user.create_user_usecase import CreateUser
from app.domain.errors import ValidationError
from app.infrastructure.repositories.in_memory.user_repository import (
    UserRepositoryInMemory,
)
from tests.support.stubs import StubHasher


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_ok():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    uc = CreateUser(repo, hasher)

    user = await uc.execute(
        email="user@example.com",
        password="StrongPass123",
        display_name="User",
    )

    assert user.email == "user@example.com"
    assert user.display_name == "User"
    assert user.password_hash == "hashed::StrongPass123"
    assert await repo.get_by_email("user@example.com") is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_duplicate_email_ko():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    uc = CreateUser(repo, hasher)

    await uc.execute(email="user@example.com", password="StrongPass123")

    with pytest.raises(ValidationError):
        await uc.execute(email="User@Example.com", password="StrongPass123")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_user_weak_password_ko():
    repo = UserRepositoryInMemory()
    hasher = StubHasher()
    uc = CreateUser(repo, hasher)

    with pytest.raises(ValidationError):
        await uc.execute(email="user@example.com", password="short")
