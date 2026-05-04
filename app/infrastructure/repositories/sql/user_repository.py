from __future__ import annotations
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.ports.user_repository import IUserRepository
from app.domain.entities.user import User
from app.infrastructure.db.models.user import UserORM


class UserRepositorySQL(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, m: UserORM) -> User:
        return User(
            id=m.id,
            email=m.email or "",
            password_hash=m.password_hash,
            display_name=m.display_name,
            is_active=m.is_active,
            email_verified=m.email_verified,
            created_at=m.created_at,
            updated_at=m.updated_at,
        )

    async def add(self, user: User) -> None:
        self.session.add(
            UserORM(
                id=user.id,
                email=user.email,
                password_hash=user.password_hash,
                display_name=user.display_name,
                is_active=user.is_active,
                email_verified=user.email_verified,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )
        await self.session.commit()

    async def update(self, user: User) -> None:
        row = await self.session.get(UserORM, user.id)
        if row is None:
            return
        row.email = user.email
        row.password_hash = user.password_hash
        row.display_name = user.display_name
        row.is_active = user.is_active
        row.email_verified = user.email_verified
        row.updated_at = user.updated_at
        await self.session.commit()

    async def get_by_id(self, user_id: UUID) -> User | None:
        row = await self.session.get(UserORM, user_id)
        return self._to_domain(row) if row else None

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(
            select(UserORM).where(UserORM.email == email.lower())
        )
        row = res.scalar_one_or_none()
        return self._to_domain(row) if row else None
