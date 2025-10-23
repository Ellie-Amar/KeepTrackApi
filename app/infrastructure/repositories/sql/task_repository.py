from __future__ import annotations
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete as sqla_delete

from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task
from app.infrastructure.db.models import TaskORM


class TaskRepositorySQL(ITaskRepository):
    """Async SQLAlchemy repository for tasks (PostgreSQL)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, task: Task) -> None:
        """Add a domain Task into the tasks table."""
        self.session.add(
            TaskORM(
                id=task.id,
                user_id=task.user_id,
                label=task.label,
                note=task.note,
                category=task.category,
                status=task.status,
                order=task.order,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        )
        await self.session.commit()

    async def list(self) -> list[Task]:
        """Return all tasks from table as domain Task."""
        result = await self.session.execute(select(TaskORM))
        rows = result.scalars().all()
        return [
            Task(
                id=row.id,
                user_id=row.user_id,
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
            user_id=row.user_id,
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
        row.user_id = task.user_id
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
