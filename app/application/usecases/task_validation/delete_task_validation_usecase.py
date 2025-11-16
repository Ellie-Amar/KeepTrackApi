from app.application.commands.delete_task_validation_command import (
    DeleteTaskValidationCommand,
)
from app.application.ports.task_validation_repository import (
    ITaskValidationRepository,
)


class DeleteTaskValidation:
    def __init__(self, repo: ITaskValidationRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: DeleteTaskValidationCommand) -> bool:
        current = await self.repo.get(cmd.validation_id)
        if current is None:
            return False
        if current.task_id != cmd.task_id or current.user_id != cmd.user_id:
            return False
        await self.repo.delete(cmd.validation_id)
        return True
