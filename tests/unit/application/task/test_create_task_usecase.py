import pytest
from uuid import uuid4
from datetime import timezone

from app.application.commands.create_task_command import CreateTaskCommand
from app.application.usecases.task.create_task_usecase import CreateTask
from app.domain.errors import ValidationError
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_ok():
    """nominal case: task is created and persisted in repo"""
    repo = TaskRepositoryInMemory()
    uc = CreateTask(repo)
    cmd = CreateTaskCommand(owner_id=uuid4(), label="Test label")

    task = await uc.execute(cmd)

    tasks = await repo.list()
    assert len(tasks) == 1
    assert task.label == "Test label"
    assert task.owner_id == cmd.owner_id
    assert task.created_at.tzinfo == timezone.utc
    assert task.status == "active"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_with_status_ok():
    """status provided by caller should be persisted"""
    repo = TaskRepositoryInMemory()
    uc = CreateTask(repo)
    cmd = CreateTaskCommand(
        owner_id=uuid4(), label="Test label", status="suspended", order=42
    )

    task = await uc.execute(cmd)

    assert task.status == "suspended"
    assert task.order == 42


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_blank_label_ko():
    """error case: empty label should raise domain validation error"""
    repo = TaskRepositoryInMemory()
    uc = CreateTask(repo)
    cmd = CreateTaskCommand(owner_id=uuid4(), label="   ")

    with pytest.raises(ValidationError):
        await uc.execute(cmd)
