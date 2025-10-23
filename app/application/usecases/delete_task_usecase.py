from __future__ import annotations
from uuid import UUID
from app.application.ports.task_repository import ITaskRepository


class DeleteTask:
    """Use case to delete a task by its uuid."""

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, task_id: UUID) -> bool:
        existing = await self.repo.get(task_id)
        if not existing:
            return False
        await self.repo.delete(task_id)
        return True
