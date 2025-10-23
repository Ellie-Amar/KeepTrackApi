from __future__ import annotations
from uuid import UUID
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class GetTask:
    """Use case to get a task."""

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, task_uuid: UUID) -> Task | None:
        return await self.repo.get(task_uuid)
