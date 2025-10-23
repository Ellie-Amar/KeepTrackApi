import pytest
from uuid import uuid4

from app.application.usecases.delete_task_usecase import DeleteTask
from app.application.usecases.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.infrastructure.repositories.in_memory.task_repository_in_memory import (
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
        CreateTaskCommand(user_id=uuid4(), label="ToDelete")
    )

    ok_first = await uc_delete.execute(created.id)
    assert ok_first is True

    ok_second = await uc_delete.execute(created.id)
    assert ok_second is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_not_found_ko():
    """Unknown task"""
    repo = TaskRepositoryInMemory()
    uc_delete = DeleteTask(repo)

    ok = await uc_delete.execute(uuid4())
    assert ok is False
