from __future__ import annotations
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete as sqla_delete, insert
from sqlalchemy.orm import selectinload

from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task, TaskWithValidations
from app.domain.entities.task_validation import TaskValidation
from app.domain.errors import ValidationError
from app.infrastructure.db.models.task import TaskORM
from app.infrastructure.db.models.task_validation import TaskValidationORM
from app.infrastructure.db.models.user import UserORM
from app.infrastructure.db.models.tasks_users import tasks_users


class TaskRepositorySQL(ITaskRepository):
    """Async SQLAlchemy repository for tasks (PostgreSQL)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, task: Task) -> None:
        """Add a domain Task into the tasks table."""

        owner = await self.session.get(UserORM, task.owner_id)
        if owner is None:
            raise ValidationError("owner_id does not refer to an existing user")

        self.session.add(
            TaskORM(
                id=task.id,
                owner_id=task.owner_id,
                label=task.label,
                note=task.note,
                category=task.category,
                status=task.status,
                order=task.order,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        )
        await self.session.flush()

        await self.session.execute(
            insert(tasks_users).values(task_id=task.id, user_id=task.owner_id)
        )

        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise

    async def list(self) -> List[Task]:
        """Return all tasks from table as domain Task."""
        result = await self.session.execute(select(TaskORM))
        rows = result.scalars().all()
        return [
            Task(
                id=row.id,
                owner_id=row.owner_id,
                label=row.label,
                note=row.note,
                category=row.category,
                status=row.status,
                order=row.order,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def list_by_user(self, user_id: UUID) -> List[Task]:
        stmt = (
            select(TaskORM)
            .join(tasks_users, tasks_users.c.task_id == TaskORM.id)
            .where(tasks_users.c.user_id == user_id)
        )
        rows = (await self.session.execute(stmt)).scalars().unique().all()
        return [
            Task(
                id=row.id,
                owner_id=row.owner_id,
                label=row.label,
                note=row.note,
                category=row.category,
                status=row.status,
                order=row.order,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

    async def list_with_validations_by_user(
        self, user_id: UUID
    ) -> List[TaskWithValidations]:
        stmt = (
            select(TaskORM)
            .options(
                selectinload(TaskORM.validations).selectinload(TaskValidationORM.user)
            )
            .join(tasks_users, tasks_users.c.task_id == TaskORM.id)
            .where(tasks_users.c.user_id == user_id)
        )
        rows = (await self.session.execute(stmt)).scalars().unique().all()
        return [
            TaskWithValidations(
                task=Task(
                    id=row.id,
                    owner_id=row.owner_id,
                    label=row.label,
                    note=row.note,
                    category=row.category,
                    status=row.status,
                    order=row.order,
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                ),
                validations=sorted(
                    [
                        TaskValidation(
                            id=validation.id,
                            task_id=validation.task_id,
                            user_id=validation.user_id,
                            note=validation.note,
                            created_at=validation.created_at,
                            updated_at=validation.updated_at,
                            user_display_name=getattr(
                                getattr(validation, "user", None), "display_name", None
                            ),
                        )
                        for validation in row.validations
                    ],
                    key=lambda item: item.created_at,
                    reverse=True,
                ),
            )
            for row in rows
        ]

    async def get_with_validations(self, task_id: UUID) -> TaskWithValidations | None:
        stmt = (
            select(TaskORM)
            .options(
                selectinload(TaskORM.validations).selectinload(TaskValidationORM.user)
            )
            .where(TaskORM.id == task_id)
        )
        row = (await self.session.execute(stmt)).scalar_one_or_none()
        if row is None:
            return None
        return TaskWithValidations(
            task=Task(
                id=row.id,
                owner_id=row.owner_id,
                label=row.label,
                note=row.note,
                category=row.category,
                status=row.status,
                order=row.order,
                created_at=row.created_at,
                updated_at=row.updated_at,
            ),
            validations=sorted(
                [
                    TaskValidation(
                        id=validation.id,
                        task_id=validation.task_id,
                        user_id=validation.user_id,
                        note=validation.note,
                        created_at=validation.created_at,
                        updated_at=validation.updated_at,
                        user_display_name=getattr(
                            getattr(validation, "user", None), "display_name", None
                        ),
                    )
                    for validation in row.validations
                ],
                key=lambda item: item.created_at,
                reverse=True,
            ),
        )

    async def get(self, task_id: UUID) -> Task | None:
        """Return a domain Task or None if not found."""
        result = await self.session.execute(
            select(TaskORM).where(TaskORM.id == task_id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return Task(
            id=row.id,
            owner_id=row.owner_id,
            label=row.label,
            note=row.note,
            category=row.category,
            status=row.status,
            order=row.order,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def update(self, task: Task) -> Task:
        row = await self.session.get(TaskORM, task.id)
        if row is None:
            return task
        row.owner_id = task.owner_id
        row.label = task.label
        row.note = task.note
        row.category = task.category
        row.status = task.status
        row.order = task.order
        row.created_at = task.created_at
        row.updated_at = task.updated_at
        await self.session.commit()
        return task

    async def delete(self, task_id: UUID) -> None:
        """Delete row by id (hard delete)."""
        await self.session.execute(sqla_delete(TaskORM).where(TaskORM.id == task_id))
        await self.session.commit()
