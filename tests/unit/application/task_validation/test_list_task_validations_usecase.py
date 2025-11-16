from uuid import uuid4

import pytest

from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.commands.list_task_validations_command import (
    ListTaskValidationsCommand,
)
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.application.usecases.task_validation.list_task_validations_usecase import (
    ListTaskValidations,
)
from app.infrastructure.repositories.in_memory.task_validation_repository import (
    TaskValidationRepositoryInMemory,
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_task_validations_usecase_returns_all_for_task_ok():
    repo = TaskValidationRepositoryInMemory()
    creator = CreateTaskValidation(repo)
    list_uc = ListTaskValidations(repo)
    task_id = uuid4()

    await creator.execute(
        CreateTaskValidationCommand(task_id=task_id, user_id=uuid4(), note="first")
    )
    await creator.execute(
        CreateTaskValidationCommand(task_id=uuid4(), user_id=uuid4(), note="other")
    )

    validations = await list_uc.execute(ListTaskValidationsCommand(task_id=task_id))

    assert len(validations) == 1
    assert validations[0].note == "first"
