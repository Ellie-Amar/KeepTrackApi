from __future__ import annotations
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.dependencies import get_db
from app.application.ports.task_repository import ITaskRepository
from app.application.usecases.create_task_usecase import CreateTask
from app.application.usecases.list_tasks_usecase import ListTasks
from app.application.usecases.get_task_usecase import GetTask
from app.application.usecases.update_task_usecase import UpdateTask
from app.application.usecases.delete_task_usecase import DeleteTask
from app.infrastructure.repositories.sql.task_repository import TaskRepositorySQL

def get_task_repo(session: AsyncSession = Depends(get_db)) -> ITaskRepository:
    """Provide concrete repository implementation for tasks."""
    return TaskRepositorySQL(session)

def get_create_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> CreateTask:
    """Provide the CreateTask use case."""
    return CreateTask(repo)

def get_list_tasks_uc(repo: ITaskRepository = Depends(get_task_repo)) -> ListTasks:
    """Provide the ListTasks use case."""
    return ListTasks(repo)

def get_get_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> GetTask:
    """Provide the GetTask use case."""
    return GetTask(repo)

def get_update_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> UpdateTask:
    """Provide the UpdateTask use case."""
    return UpdateTask(repo)

def get_delete_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> DeleteTask:
    """Provide the DeleteTask use case."""
    return DeleteTask(repo)
