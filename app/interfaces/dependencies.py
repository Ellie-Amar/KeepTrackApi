from __future__ import annotations
from datetime import timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.user_repository import IUserRepository
from app.application.usecases.auth.login_user_usecase import LoginUserUseCase
from app.application.usecases.user.create_user_usecase import CreateUser
from app.config.settings import settings
from app.infrastructure.adapters.argon2_password_hasher import Argon2PasswordHasher
from app.infrastructure.adapters.jwt_token_service import JwtTokenService
from app.infrastructure.db.dependencies import get_db
from app.application.ports.task_repository import ITaskRepository
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.list_tasks_usecase import ListTasks
from app.application.usecases.task.get_task_usecase import GetTask
from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task.delete_task_usecase import DeleteTask
from app.infrastructure.repositories.sql.task_repository import TaskRepositorySQL
from app.infrastructure.repositories.sql.user_repository import UserRepositorySQL

# --- Auth ---


def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


def get_token_service():
    return JwtTokenService(
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        access_ttl=timedelta(minutes=settings.jwt_access_ttl_minutes),
    )


# --- Task ---
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


# --- User ---


def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepositorySQL(session)


def get_create_user_uc(
    repo=Depends(get_user_repo), hasher=Depends(get_password_hasher)
):
    return CreateUser(repo, hasher)


def get_login_user_uc(
    repo: IUserRepository = Depends(get_user_repo),
    hasher=Depends(get_password_hasher),
    token=Depends(get_token_service),
):
    return LoginUserUseCase(repo, hasher, token)
