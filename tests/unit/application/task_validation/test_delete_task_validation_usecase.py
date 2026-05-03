from uuid import uuid4

import pytest

from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.commands.delete_task_validation_command import (
    DeleteTaskValidationCommand,
)
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.application.usecases.task_validation.delete_task_validation_usecase import (
    DeleteTaskValidation,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_validation_usecase_removes_entry_ok():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    del_uc = DeleteTaskValidation(repo)

    existing = await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note=None)
    )
    cmd = DeleteTaskValidationCommand(
        validation_id=existing.id,
        task_id=existing.task_id,
        user_id=existing.user_id,
    )

    success = await del_uc.execute(cmd)

    assert success is True
    assert await repo.get(existing.id) is None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_validation_usecase_rejects_foreign_user_ko():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    del_uc = DeleteTaskValidation(repo)

    existing = await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note=None)
    )
    cmd = DeleteTaskValidationCommand(
        validation_id=existing.id,
        task_id=existing.task_id,
        user_id=uuid4(),
    )

    success = await del_uc.execute(cmd)

    assert success is False
    assert await repo.get(existing.id) is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_delete_task_validation_usecase_rejects_wrong_task_ko():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    del_uc = DeleteTaskValidation(repo)

    existing = await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note=None)
    )
    cmd = DeleteTaskValidationCommand(
        validation_id=existing.id,
        task_id=uuid4(),
        user_id=existing.user_id,
    )

    success = await del_uc.execute(cmd)

    assert success is False
    assert await repo.get(existing.id) is not None
