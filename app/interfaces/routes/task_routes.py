from __future__ import annotations
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException

from app.interfaces.view_models.task_view_model import TaskCreate, TaskRead
from app.interfaces.view_models.task_view_model import TaskUpdate

from app.application.usecases.create_task_usecase import CreateTask
from app.application.usecases.list_tasks_usecase import ListTasks
from app.application.usecases.get_task_usecase import GetTask
from app.application.usecases.update_task_usecase import UpdateTask
from app.application.usecases.delete_task_usecase import DeleteTask

from app.application.commands.create_task_command import CreateTaskCommand
from app.application.commands.update_task_command import UpdateTaskCommand

from app.interfaces.dependencies import (
    get_create_task_uc,
    get_list_tasks_uc,
    get_get_task_uc,
    get_update_task_uc,
    get_delete_task_uc,
)


router = APIRouter(prefix="/v1/tasks", tags=["tasks"])


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    payload: TaskCreate,
    use_case: CreateTask = Depends(get_create_task_uc),
):
    """Create a new task."""
    task = await use_case.execute(CreateTaskCommand(**payload.model_dump()))
    return task


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    use_case: ListTasks = Depends(get_list_tasks_uc),
):
    """List all tasks."""
    tasks = await use_case.execute()
    return tasks


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID,
    use_case: GetTask = Depends(get_get_task_uc),
):
    """Get a task by its uuid"""
    task = await use_case.execute(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    use_case_update: UpdateTask = Depends(get_update_task_uc),
):
    """Patch a task by its uuid"""
    updated = await use_case_update.execute(
        UpdateTaskCommand(id=task_id, **payload.model_dump(exclude_unset=True))
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    use_case_delete: DeleteTask = Depends(get_delete_task_uc),
):
    """Delete a task by its uuid"""
    deleted = await use_case_delete.execute(task_id)
    if deleted is False:
        raise HTTPException(status_code=404, detail="Task not found")
    return None
