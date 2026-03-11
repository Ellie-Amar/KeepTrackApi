from __future__ import annotations

from app.application.commands.get_task_command import GetTaskCommand
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class GetTask:
    """
    Fetch a task by id.
    """

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, command: GetTaskCommand) -> Task | None:
        return await self.repo.get(command.task_id)
