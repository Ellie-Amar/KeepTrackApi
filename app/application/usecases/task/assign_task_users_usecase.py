from __future__ import annotations
from uuid import UUID

from app.application.commands.assign_task_users_command import (
    AssignTaskUsersCommand,
)
from app.application.ports.task_repository import ITaskRepository
from app.application.ports.user_repository import IUserRepository
from app.domain.entities.user import User
from app.domain.errors import ValidationError


class AssignTaskUsers:
    def __init__(self, task_repo: ITaskRepository, user_repo: IUserRepository) -> None:
        self.task_repo = task_repo
        self.user_repo = user_repo

    async def execute(self, cmd: AssignTaskUsersCommand) -> list[User] | None:
        task = await self.task_repo.get(cmd.task_id)
        if task is None:
            return None

        if task.owner_id != cmd.requester_id:
            raise ValidationError("Only the owner can assign users")

        normalized_emails = list(
            dict.fromkeys(email.lower() for email in cmd.user_emails)
        )

        users: dict[UUID, User] = {}
        for email in normalized_emails:
            user = await self.user_repo.get_by_email(email)
            if user is None:
                raise ValidationError("User not found")
            users[user.id] = user

        user_ids = list(users.keys())

        if any(user_id == task.owner_id for user_id in user_ids):
            raise ValidationError("The owner is already assigned to the task")

        current_assignees = set(await self.task_repo.list_assignees(cmd.task_id))
        already_assigned = [uid for uid in user_ids if uid in current_assignees]
        if already_assigned:
            raise ValidationError("One or more users are already assigned")

        for user_id in user_ids:
            await self.task_repo.add_assignee(cmd.task_id, user_id)

        return [users[user_id] for user_id in user_ids]
