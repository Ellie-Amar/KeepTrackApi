import pytest
from uuid import uuid4

from app.application.usecases.get_task_usecase import GetTask
from app.application.usecases.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.infrastructure.repositories.in_memory.task_repository_in_memory import TaskRepositoryInMemory


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_found_ok():
    """Nominal case"""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_get = GetTask(repo)

    created = await uc_create.execute(CreateTaskCommand(user_id=uuid4(), label="Read"))
    result = await uc_get.execute(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.label == "Read"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_task_not_found_ko():
    """Unknown task"""
    repo = TaskRepositoryInMemory()
    uc_get = GetTask(repo)

    result = await uc_get.execute(uuid4())
    assert result is None
