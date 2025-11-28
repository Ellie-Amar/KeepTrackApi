from __future__ import annotations
from uuid import UUID

from fastapi import APIRouter, Depends, status, HTTPException

from app.application.commands.assign_task_users_command import (
    AssignTaskUsersCommand,
)
from app.application.commands.delete_task_command import DeleteTaskCommand
from app.application.commands.list_task_assignees_command import (
    ListTaskAssigneesCommand,
)
from app.application.commands.list_tasks_command import ListTasksCommand
from app.application.commands.remove_task_user_command import RemoveTaskUserCommand
from app.domain.entities.task import Task, TaskWithValidations
from app.domain.entities.user import User
from app.interfaces.security import (
    get_current_user,
    require_task_access,
    require_task_with_validations,
    require_task_owner,
)
from app.interfaces.view_models.task_view_model import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.interfaces.view_models.task_assignee_view_model import TaskAssigneesCreate
from app.interfaces.view_models.user_view_model import UserRead

from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.list_task_assignees_usecase import (
    ListTaskAssignees,
)
from app.application.usecases.task.list_tasks_with_validations_usecase import (
    ListTasksWithValidations,
)
from app.application.usecases.task.assign_task_users_usecase import AssignTaskUsers
from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task.remove_task_user_usecase import RemoveTaskUser
from app.application.usecases.task.delete_task_usecase import DeleteTask
from app.domain.errors import ValidationError

from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.update_task_command import UpdateTaskCommand

from app.interfaces.dependencies import (
    get_create_task_uc,
    get_assign_task_users_uc,
    get_list_task_assignees_uc,
    get_list_tasks_with_validations_uc,
    get_remove_task_user_uc,
    get_update_task_uc,
    get_delete_task_uc,
)


router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    usecase: CreateTask = Depends(get_create_task_uc),
    current_user: User = Depends(get_current_user),
):
    """Create a new task owned by the authenticated user."""
    task = await usecase.execute(
        CreateTaskCommand(**payload.model_dump(), owner_id=current_user.id)
    )
    return task


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    usecase_get: ListTasksWithValidations = Depends(get_list_tasks_with_validations_uc),
    current_user=Depends(get_current_user),
):
    """List tasks visible to the authenticated user, including validation history."""
    results = await usecase_get.execute(ListTasksCommand(user_id=current_user.id))
    return [TaskRead.from_task_with_validations(item, current_user) for item in results]


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    item: TaskWithValidations = Depends(require_task_with_validations),
    current_user: User = Depends(get_current_user),
):
    """Get a task by its uuid"""
    if not item:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskRead.from_task_with_validations(item, current_user)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    payload: TaskUpdate,
    task: Task = Depends(require_task_access),
    usecase_update: UpdateTask = Depends(get_update_task_uc),
):
    """Patch a task by its uuid"""
    updated = await usecase_update.execute(
        UpdateTaskCommand(id=task.id, **payload.model_dump(exclude_unset=True))
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task: Task = Depends(require_task_access),
    usecase_delete: DeleteTask = Depends(get_delete_task_uc),
):
    """Delete a task by its uuid"""
    deleted = await usecase_delete.execute(DeleteTaskCommand(task_id=task.id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return None


@router.get("/{task_id}/assignees", response_model=list[UserRead])
async def list_task_assignees(
    task: Task = Depends(require_task_access),
    uc: ListTaskAssignees = Depends(get_list_task_assignees_uc),
):
    """List users assigned to a task (participants)."""
    users = await uc.execute(ListTaskAssigneesCommand(task_id=task.id))
    return [UserRead.model_validate(user) for user in users]


@router.post(
    "/{task_id}/assignees",
    response_model=list[UserRead],
    status_code=status.HTTP_201_CREATED,
)
async def assign_task_users(
    payload: TaskAssigneesCreate,
    task: Task = Depends(require_task_owner),
    current_user: User = Depends(get_current_user),
    uc: AssignTaskUsers = Depends(get_assign_task_users_uc),
):
    """Assign one or many users to a task (owner only)."""
    try:
        users = await uc.execute(
            AssignTaskUsersCommand(
                task_id=task.id,
                requester_id=current_user.id,
                user_emails=payload.user_emails,
            )
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return [UserRead.model_validate(user) for user in users]


@router.delete(
    "/{task_id}/assignees/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unassign_task_user(
    user_id: UUID,
    task: Task = Depends(require_task_owner),
    current_user: User = Depends(get_current_user),
    uc: RemoveTaskUser = Depends(get_remove_task_user_uc),
):
    """Remove an assignee from a task (owner only)."""
    try:
        removed = await uc.execute(
            RemoveTaskUserCommand(
                task_id=task.id,
                requester_id=current_user.id,
                user_id=user_id,
            )
        )
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if removed is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not assigned"
        )

    return None
