from __future__ import annotations
from typing import List
from app.application.commands.list_tasks_command import ListTasksCommand
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class ListTasks:
    """List tasks visible to a given user (participant or owner)."""

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, command: ListTasksCommand) -> List[Task]:
        return await self.repo.list_by_user(command.user_id)
