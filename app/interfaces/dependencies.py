from __future__ import annotations
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dependencies import get_db
from app.application.ports.task_repository import ITaskRepository
from app.application.usecases.create_task_usecase import CreateTask
from app.application.usecases.list_tasks_usecase import ListTasks
from app.infrastructure.repositories.sql.task_repository import TaskRepositorySQL

def get_task_repo(session: AsyncSession = Depends(get_db)) -> ITaskRepository:
    """Provide concrete repository implementation for tasks."""

    return TaskRepositorySQL(session)

def get_create_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> CreateTask:
    return CreateTask(repo)

def get_list_tasks_uc(repo: ITaskRepository = Depends(get_task_repo)) -> ListTasks:
    return ListTasks(repo)
