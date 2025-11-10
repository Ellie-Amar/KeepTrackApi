from __future__ import annotations
from typing import List
from uuid import UUID
from app.application.ports.user_repository import IUserRepository
from app.domain.entities.user import User


class UserRepositoryInMemory(IUserRepository):
    def __init__(self) -> None:
        self.users: List[User] = []

    async def add(self, user: User) -> None:
        for i, u in enumerate(self.users):
            if u.id == user.id:
                self.users[i] = user
                break
        else:
            self.users.append(user)

    async def get_by_id(self, user_id: UUID) -> User | None:
        for u in self.users:
            if u.id == user_id:
                return u
        return None

    async def get_by_email(self, email: str) -> User | None:
        e = (email or "").strip().lower()
        for u in self.users:
            if u.email == e:
                return u
        return None
