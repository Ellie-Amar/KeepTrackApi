from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.ports.task_validation_repository import (
    ITaskValidationRepository,
)
from app.domain.entities.task_validation import TaskValidation


class CreateTaskValidation:
    def __init__(self, repo: ITaskValidationRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: CreateTaskValidationCommand) -> TaskValidation:
        validation = TaskValidation.new(
            task_id=cmd.task_id,
            user_id=cmd.user_id,
            note=cmd.note,
        )
        return await self.repo.add(validation)
