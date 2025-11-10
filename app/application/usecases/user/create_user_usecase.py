from __future__ import annotations
from app.application.ports.user_repository import IUserRepository
from app.application.ports.password_hasher import IPasswordHasher
from app.domain.entities.user import User
from app.domain.errors import ValidationError


class CreateUser:
    def __init__(self, repo: IUserRepository, hasher: IPasswordHasher) -> None:
        self.repo = repo
        self.hasher = hasher

    async def execute(
        self, email: str, password: str, display_name: str | None = None
    ) -> User:

        if not password or len(password) < 8:
            raise ValidationError("Password too short")

        if await self.repo.get_by_email(email.lower()):
            raise ValidationError("Email already exists")

        password_hash = self.hasher.hash(password)
        user = User.new(
            email=email, password_hash=password_hash, display_name=display_name
        )
        await self.repo.add(user)
        return user
