from __future__ import annotations
from fastapi import APIRouter, Depends, status

from app.interfaces.view_models.task_view_model import TaskCreate, TaskRead
from app.application.usecases.create_task_usecase import CreateTask
from app.application.usecases.list_tasks_usecase import ListTasks
from app.application.commands.create_task_command import CreateTaskCommand
from app.interfaces.dependencies import get_create_task_uc, get_list_tasks_uc

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
