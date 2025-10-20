from __future__ import annotations

import pytest
from uuid import uuid4

from app.application.usecases.list_tasks_usecase import ListTasks
from app.application.usecases.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.infrastructure.repositories.in_memory.task_repository_in_memory import (
    TaskRepositoryInMemory,
)

@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tasks_empty_ok():
    """Nominal: listing on empty repo returns an empty list."""
    repo = TaskRepositoryInMemory()
    uc_list = ListTasks(repo)

    items = await uc_list.execute()

    assert isinstance(items, list)
    assert items == []

@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tasks_after_creations_ok():
    """Nominal: after creating tasks, list returns them."""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_list = ListTasks(repo)

    await uc_create.execute(CreateTaskCommand(user_id=uuid4(), label="Drink water"))
    await uc_create.execute(CreateTaskCommand(user_id=uuid4(), label="Walk 10 min"))

    items = await uc_list.execute()

    labels = {t.label for t in items}
    assert labels == {"Drink water", "Walk 10 min"}
    assert len(items) == 2
