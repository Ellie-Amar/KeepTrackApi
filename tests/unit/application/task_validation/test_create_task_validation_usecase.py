from uuid import uuid4

import pytest

from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_task_validation_usecase_persists_note_ok():
    repo = TaskValidationRepositoryInMemory()
    uc = CreateTaskValidation(repo)
    cmd = CreateTaskValidationCommand(
        task_id=uuid4(),
        user_id=uuid4(),
        note="  completed ",
    )

    validation = await uc.execute(cmd)

    assert validation.note == "completed"
    stored = await repo.get(validation.id)
    assert stored is not None
    assert stored.note == "completed"
