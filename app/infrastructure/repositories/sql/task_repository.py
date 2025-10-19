from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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
        rows: list[tuple[TaskORM]] = result.all()  # type: ignore

        return [
            Task(
                id=row[0].id,
                user_id=row[0].user_id,
                label=row[0].label,
                note=row[0].note,
                category=row[0].category,
                status=row[0].status,
                order=row[0].order,
                created_at=row[0].created_at,
                updated_at=row[0].updated_at,
            )
            for row in rows
        ]
