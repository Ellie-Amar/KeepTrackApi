from __future__ import annotations

from collections.abc import Iterable
from typing import Sequence
from uuid import UUID

from sqlalchemy import delete as sqla_delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.application.ports.task_validation_repository import ITaskValidationRepository
from app.domain.entities.task_validation import TaskValidation
from app.infrastructure.db.models.task_validation import TaskValidationORM


class TaskValidationRepositorySQL(ITaskValidationRepository):
    """Async SQLAlchemy repository for task validations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_domain(self, row: TaskValidationORM) -> TaskValidation:
        return TaskValidation(
            id=row.id,
            task_id=row.task_id,
            user_id=row.user_id,
            note=row.note,
            created_at=row.created_at,
            updated_at=row.updated_at,
            user_display_name=getattr(row.user, "display_name", None),
        )

    async def add(self, validation: TaskValidation) -> TaskValidation:
        self.session.add(
            TaskValidationORM(
                id=validation.id,
                task_id=validation.task_id,
                user_id=validation.user_id,
                note=validation.note,
                created_at=validation.created_at,
                updated_at=validation.updated_at,
            )
        )
        await self.session.commit()
        return validation

    async def get(self, validation_id: UUID) -> TaskValidation | None:
        stmt = (
            select(TaskValidationORM)
            .options(selectinload(TaskValidationORM.user))
            .where(TaskValidationORM.id == validation_id)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def list_by_task(self, task_id: UUID) -> list[TaskValidation]:
        result = await self.session.execute(
            select(TaskValidationORM)
            .options(selectinload(TaskValidationORM.user))
            .where(TaskValidationORM.task_id == task_id)
            .order_by(TaskValidationORM.created_at.desc())
        )
        rows: Sequence[TaskValidationORM] = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    async def list_by_tasks(self, task_ids: Iterable[UUID]) -> list[TaskValidation]:
        ids = list(task_ids)
        if not ids:
            return []
        result = await self.session.execute(
            select(TaskValidationORM)
            .options(selectinload(TaskValidationORM.user))
            .where(TaskValidationORM.task_id.in_(ids))
            .order_by(
                TaskValidationORM.task_id,
                TaskValidationORM.created_at.desc(),
            )
        )
        rows: Sequence[TaskValidationORM] = result.scalars().all()
        return [self._to_domain(row) for row in rows]

    async def update(self, validation: TaskValidation) -> TaskValidation:
        row = await self.session.get(TaskValidationORM, validation.id)
        if row is None:
            return validation
        row.note = validation.note
        row.updated_at = validation.updated_at
        await self.session.commit()
        return validation

    async def delete(self, validation_id: UUID) -> None:
        await self.session.execute(
            sqla_delete(TaskValidationORM).where(TaskValidationORM.id == validation_id)
        )
        await self.session.commit()
