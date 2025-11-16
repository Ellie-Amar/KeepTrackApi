from __future__ import annotations

from typing import List

from app.application.commands.list_tasks_command import ListTasksCommand
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import TaskWithValidations


class ListTasksWithValidations:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(self, command: ListTasksCommand) -> List[TaskWithValidations]:
        return await self.task_repo.list_with_validations_by_user(command.user_id)
