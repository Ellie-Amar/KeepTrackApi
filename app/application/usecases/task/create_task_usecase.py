from app.application.commands.create_task_command import CreateTaskCommand
from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task


class CreateTask:
    def __init__(self, repo: ITaskRepository) -> None:
        self.repo = repo

    async def execute(self, cmd: CreateTaskCommand) -> Task:
        task = Task.new(
            owner_id=cmd.owner_id,
            label=cmd.label,
            category=cmd.category,
            note=cmd.note,
            status=cmd.status,
            order=cmd.order,
        )

        await self.repo.add(task)

        return task
