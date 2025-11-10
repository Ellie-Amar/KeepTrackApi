from __future__ import annotations

import pytest
from uuid import uuid4

from app.application.usecases.task.list_tasks_usecase import ListTasks
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.list_tasks_command import ListTasksCommand
from app.infrastructure.repositories.in_memory.task_repository import (
    TaskRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tasks_empty_ok():
    """Nominal: listing on empty repo returns an empty list."""
    repo = TaskRepositoryInMemory()
    uc_list = ListTasks(repo)
    user_id = uuid4()

    items = await uc_list.execute(ListTasksCommand(user_id=user_id))

    assert isinstance(items, list)
    assert items == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_tasks_after_creations_ok():
    """Nominal: after creating tasks, list returns them."""
    repo = TaskRepositoryInMemory()
    uc_create = CreateTask(repo)
    uc_list = ListTasks(repo)
    user_id = uuid4()
    other_user_id = uuid4()

    await uc_create.execute(CreateTaskCommand(owner_id=user_id, label="Drink water"))
    await uc_create.execute(CreateTaskCommand(owner_id=user_id, label="Walk 10 min"))
    await uc_create.execute(CreateTaskCommand(owner_id=other_user_id, label="Skip"))

    items = await uc_list.execute(ListTasksCommand(user_id=user_id))

    labels = {t.label for t in items}
    assert labels == {"Drink water", "Walk 10 min"}
    assert len(items) == 2
