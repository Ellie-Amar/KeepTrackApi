from __future__ import annotations
from app.application.commands.delete_task_command import DeleteTaskCommand
from app.application.ports.task_repository import ITaskRepository


class DeleteTask:
    """Use case to delete a task by its uuid."""

    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, command: DeleteTaskCommand) -> bool:
        existing = await self.repo.get(command.task_id)
        if not existing:
            return False
        await self.repo.delete(command.task_id)
        return True
