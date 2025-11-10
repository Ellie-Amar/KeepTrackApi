import pytest
from uuid import uuid4

from app.application.usecases.task.delete_task_usecase import DeleteTask
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.delete_task_command import DeleteTaskCommand
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_ok_then_ko():
    """Nomical case"""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_delete = DeleteTask(repo)

    created = await uc_create.execute(
        CreateTaskCommand(owner_id=uuid4(), label="ToDelete")
    )

    ok_first = await uc_delete.execute(DeleteTaskCommand(task_id=created.id))
    assert ok_first is True

    ok_second = await uc_delete.execute(DeleteTaskCommand(task_id=created.id))
    assert ok_second is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_not_found_ko():
    """Unknown task"""
    repo = TaskRepositoryInMemory()
    uc_delete = DeleteTask(repo)

    ok = await uc_delete.execute(DeleteTaskCommand(task_id=uuid4()))
    assert ok is False
