import pytest
from uuid import uuid4

from app.application.usecases.task.get_task_usecase import GetTask
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.get_task_command import GetTaskCommand
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_found_ok():
    """Nominal case"""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_get = GetTask(repo)

    created = await uc_create.execute(CreateTaskCommand(owner_id=uuid4(), label="Read"))
    result = await uc_get.execute(GetTaskCommand(task_id=created.id))

    assert result is not None
    assert result.id == created.id
    assert result.label == "Read"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_not_found_ko():
    """Unknown task"""
    repo = TaskRepositoryInMemory()
    uc_get = GetTask(repo)

    result = await uc_get.execute(GetTaskCommand(task_id=uuid4()))
    assert result is None
