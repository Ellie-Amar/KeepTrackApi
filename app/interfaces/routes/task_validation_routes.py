from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID

from app.application.commands.create_task_validation_command import (
    CreateTaskValidationCommand,
)
from app.application.commands.delete_task_validation_command import (
    DeleteTaskValidationCommand,
)
from app.application.commands.update_task_validation_command import (
    UpdateTaskValidationCommand,
)
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.application.usecases.task_validation.delete_task_validation_usecase import (
    DeleteTaskValidation,
)
from app.application.usecases.task_validation.update_task_validation_usecase import (
    UpdateTaskValidation,
)
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.interfaces.dependencies import (
    get_create_task_validation_uc,
    get_delete_task_validation_uc,
    get_update_task_validation_uc,
)
from app.interfaces.security import get_current_user, require_task_access
from app.interfaces.view_models.task_validation_view_model import (
    TaskValidationCreate,
    TaskValidationRead,
    TaskValidationUpdate,
)

router = APIRouter(
    prefix="/v1/tasks/{task_id}/validations",
    tags=["task-validations"],
)


@router.post("", response_model=TaskValidationRead, status_code=status.HTTP_201_CREATED)
async def create_task_validation(
    payload: TaskValidationCreate,
    task: Task = Depends(require_task_access),
    current_user: User = Depends(get_current_user),
    usecase: CreateTaskValidation = Depends(get_create_task_validation_uc),
):
    """Register a validation for the given task on behalf of the authenticated user."""
    command = CreateTaskValidationCommand(
        task_id=task.id,
        user_id=current_user.id,
        note=payload.note,
    )
    created = await usecase.execute(command)
    return TaskValidationRead.from_entity_for_user(created, current_user)


@router.patch(
    "/{validation_id}",
    response_model=TaskValidationRead,
    status_code=status.HTTP_200_OK,
)
async def update_task_validation(
    validation_id: UUID,
    payload: TaskValidationUpdate,
    task: Task = Depends(require_task_access),
    current_user: User = Depends(get_current_user),
    usecase: UpdateTaskValidation = Depends(get_update_task_validation_uc),
):
    """Update the note of an existing validation owned by the current user."""
    command = UpdateTaskValidationCommand(
        validation_id=validation_id,
        task_id=task.id,
        user_id=current_user.id,
        note=payload.note,
    )
    updated = await usecase.execute(command)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return TaskValidationRead.from_entity_for_user(updated, current_user)


@router.delete(
    "/{validation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task_validation(
    validation_id: UUID,
    task: Task = Depends(require_task_access),
    current_user: User = Depends(get_current_user),
    usecase: DeleteTaskValidation = Depends(get_delete_task_validation_uc),
):
    """Delete one of the caller's validations for the given task."""
    command = DeleteTaskValidationCommand(
        validation_id=validation_id,
        task_id=task.id,
        user_id=current_user.id,
    )
    success = await usecase.execute(command)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
