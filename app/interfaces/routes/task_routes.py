from __future__ import annotations
from fastapi import APIRouter, Depends, status, HTTPException

from app.application.commands.delete_task_command import DeleteTaskCommand
from app.application.commands.list_tasks_command import ListTasksCommand
from app.domain.entities.task import Task
from app.domain.entities.user import User
from app.interfaces.security import get_current_user, require_task_access
from app.interfaces.view_models.task_view_model import TaskCreate, TaskRead
from app.interfaces.view_models.task_view_model import TaskUpdate

from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.list_tasks_usecase import ListTasks
from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task.delete_task_usecase import DeleteTask

from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.update_task_command import UpdateTaskCommand

from app.interfaces.dependencies import (
    get_create_task_uc,
    get_list_tasks_uc,
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
    usecase_get: ListTasks = Depends(get_list_tasks_uc),
    current_user=Depends(get_current_user),
):
    """List tasks visible to the authenticated user."""
    tasks = await usecase_get.execute(ListTasksCommand(user_id=current_user.id))
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task: Task = Depends(require_task_access),
):
    """Get a task by its uuid"""
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


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
