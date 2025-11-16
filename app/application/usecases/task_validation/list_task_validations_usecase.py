from app.application.commands.list_task_validations_command import (
    ListTaskValidationsCommand,
)
from app.application.ports.task_validation_repository import (
    ITaskValidationRepository,
)
from app.domain.entities.task_validation import TaskValidation


class ListTaskValidations:
    def __init__(self, repo: ITaskValidationRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: ListTaskValidationsCommand) -> list[TaskValidation]:
        return await self.repo.list_by_task(cmd.task_id)
