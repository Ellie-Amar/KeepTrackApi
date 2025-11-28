from __future__ import annotations

from app.application.commands.remove_task_user_command import (
    RemoveTaskUserCommand,
)
from app.application.ports.task_repository import ITaskRepository
from app.domain.errors import ValidationError


class RemoveTaskUser:
    def __init__(self, task_repo: ITaskRepository) -> None:
        self.task_repo = task_repo

    async def execute(self, cmd: RemoveTaskUserCommand) -> bool | None:
        task = await self.task_repo.get(cmd.task_id)
        if task is None:
            return None

        if task.owner_id != cmd.requester_id:
            raise ValidationError("Only the owner can unassign a user")

        if cmd.user_id == task.owner_id:
            raise ValidationError("Cannot unassign the owner")

        assignees = set(await self.task_repo.list_assignees(cmd.task_id))
        if cmd.user_id not in assignees:
            return False

        await self.task_repo.remove_assignee(cmd.task_id, cmd.user_id)
        return True
