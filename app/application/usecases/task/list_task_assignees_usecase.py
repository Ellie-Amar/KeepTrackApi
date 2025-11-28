from __future__ import annotations

from app.application.commands.list_task_assignees_command import (
    ListTaskAssigneesCommand,
)
from app.application.ports.task_repository import ITaskRepository
from app.application.ports.user_repository import IUserRepository
from app.domain.entities.user import User


class ListTaskAssignees:
    def __init__(self, task_repo: ITaskRepository, user_repo: IUserRepository) -> None:
        self.task_repo = task_repo
        self.user_repo = user_repo

    async def execute(self, cmd: ListTaskAssigneesCommand) -> list[User]:
        assignee_ids = await self.task_repo.list_assignees(cmd.task_id)
        users: list[User] = []
        for user_id in assignee_ids:
            user = await self.user_repo.get_by_id(user_id)
            if user:
                users.append(user)
        return users
