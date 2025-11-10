import pytest
from uuid import uuid4

from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.update_task_command import UpdateTaskCommand
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_partial_ok():
    """Nominal case"""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_update = UpdateTask(repo)

    created = await uc_create.execute(
        CreateTaskCommand(owner_id=uuid4(), label="Before")
    )

    updated = await uc_update.execute(
        UpdateTaskCommand(id=created.id, label="After", note="updated")
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.label == "After"
    assert updated.note == "updated"
    assert updated.updated_at != created.updated_at


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_not_found_ko():
    """Unknown task"""
    repo = TaskRepositoryInMemory()
    uc_update = UpdateTask(repo)

    result = await uc_update.execute(UpdateTaskCommand(id=uuid4(), label="Nope"))
    assert result is None
