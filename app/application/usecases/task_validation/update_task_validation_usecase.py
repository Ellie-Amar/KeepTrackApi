from app.application.commands.update_task_validation_command import (
    UpdateTaskValidationCommand,
)
from app.application.ports.task_validation_repository import (
    ITaskValidationRepository,
)
from app.domain.entities.task_validation import TaskValidation


class UpdateTaskValidation:
    def __init__(self, repo: ITaskValidationRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: UpdateTaskValidationCommand) -> TaskValidation | None:
        current = await self.repo.get(cmd.validation_id)
        if current is None:
            return None
        if current.task_id != cmd.task_id or current.user_id != cmd.user_id:
            return None
        updated = current.with_note(cmd.note)
        if updated is current:
            return current
        return await self.repo.update(updated)
