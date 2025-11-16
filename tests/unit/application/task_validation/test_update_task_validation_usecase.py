from uuid import uuid4

import pytest

from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.commands.update_task_validation_command import (
    UpdateTaskValidationCommand,
)
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.application.usecases.task_validation.update_task_validation_usecase import (
    UpdateTaskValidation,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_validation_usecase_updates_note_ok():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    upd_uc = UpdateTaskValidation(repo)

    existing = await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note="old")
    )
    cmd = UpdateTaskValidationCommand(
        validation_id=existing.id,
        task_id=existing.task_id,
        user_id=existing.user_id,
        note="new note",
    )

    updated = await upd_uc.execute(cmd)

    assert updated is not None
    assert updated.note == "new note"
    stored = await repo.get(existing.id)
    assert stored is not None and stored.note == "new note"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_task_validation_usecase_rejects_foreign_user_ko():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    upd_uc = UpdateTaskValidation(repo)

    existing = await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note="old")
    )
    cmd = UpdateTaskValidationCommand(
        validation_id=existing.id,
        task_id=existing.task_id,
        user_id=uuid4(),
        note="won't work",
    )

    result = await upd_uc.execute(cmd)

    assert result is None
    stored = await repo.get(existing.id)
    assert stored is not None and stored.note == "old"
