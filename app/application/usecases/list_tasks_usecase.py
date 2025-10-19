from __future__ import annotations
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class ListTasks:
    """Use case to list all tasks."""

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self) -> list[Task]:
        """Return all tasks from repository."""
        return await self.repo.list()
