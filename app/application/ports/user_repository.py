from __future__ import annotations
from typing import Protocol
from uuid import UUID
from app.domain.entities.user import User


class IUserRepository(Protocol):
    async def add(self, user: User) -> None: ...
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
