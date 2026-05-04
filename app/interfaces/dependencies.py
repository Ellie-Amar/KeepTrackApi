from __future__ import annotations
from datetime import timedelta
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.email_sender import IEmailSender
from app.application.ports.task_validation_repository import (
    ITaskValidationRepository,
)
from app.application.ports.token_service import ITokenService
from app.application.ports.user_repository import IUserRepository
from app.application.usecases.auth.login_user_usecase import LoginUserUseCase
from app.application.usecases.user.create_user_usecase import CreateUser
from app.application.usecases.user.verify_user_email_usecase import VerifyUserEmail
from app.application.usecases.auth.refresh_token_usecase import RefreshTokenUseCase
from app.config.settings import settings
from app.infrastructure.adapters.argon2_password_hasher import Argon2PasswordHasher
from app.infrastructure.adapters.jwt_token_service import JwtTokenService
from app.infrastructure.adapters.smtp_email_sender import (
    NoopEmailSender,
    SmtpEmailSender,
)
from app.infrastructure.db.dependencies import get_db
from app.application.ports.task_repository import ITaskRepository
from app.application.usecases.task.create_task_usecase import CreateTask
from app.application.usecases.task.list_tasks_usecase import ListTasks
from app.application.usecases.task.list_tasks_with_validations_usecase import (
    ListTasksWithValidations,
)
from app.application.usecases.task.get_task_usecase import GetTask
from app.application.usecases.task.update_task_usecase import UpdateTask
from app.application.usecases.task.assign_task_users_usecase import AssignTaskUsers
from app.application.usecases.task.list_task_assignees_usecase import (
    ListTaskAssignees,
)
from app.application.usecases.task.remove_task_user_usecase import RemoveTaskUser
from app.application.usecases.task_validation.create_task_validation_usecase import (
    CreateTaskValidation,
)
from app.application.usecases.task_validation.delete_task_validation_usecase import (
    DeleteTaskValidation,
)
from app.application.usecases.task_validation.list_task_validations_usecase import (
    ListTaskValidations,
)
from app.application.usecases.task_validation.update_task_validation_usecase import (
    UpdateTaskValidation,
)
from app.application.usecases.task.delete_task_usecase import DeleteTask
from app.infrastructure.repositories.sql.task_repository import TaskRepositorySQL
from app.infrastructure.repositories.sql.task_validation_repository import (
    TaskValidationRepositorySQL,
)
from app.infrastructure.repositories.sql.user_repository import UserRepositorySQL

# --- Auth ---


def get_password_hasher() -> Argon2PasswordHasher:
    return Argon2PasswordHasher()


def get_token_service():
    assert settings.jwt_secret is not None
    return JwtTokenService(
        secret=settings.jwt_secret,
        issuer=settings.jwt_issuer,
        access_ttl=timedelta(minutes=settings.jwt_access_ttl_minutes),
        refresh_ttl=timedelta(minutes=settings.jwt_refresh_ttl_minutes),
        email_verification_ttl=timedelta(
            minutes=settings.jwt_email_verification_ttl_minutes
        ),
    )


def get_email_sender() -> IEmailSender:
    config_values = (
        settings.smtp_host,
        settings.smtp_username,
        settings.smtp_password,
        settings.smtp_sender_email,
    )
    if any(not value for value in config_values):
        return NoopEmailSender()
    return SmtpEmailSender(
        host=str(settings.smtp_host),
        port=settings.smtp_port,
        username=str(settings.smtp_username),
        password=str(settings.smtp_password),
        sender_email=str(settings.smtp_sender_email),
        sender_name=settings.smtp_sender_name,
    )


# --- User ---


def get_user_repo(session: AsyncSession = Depends(get_db)):
    return UserRepositorySQL(session)


def get_create_user_uc(
    repo=Depends(get_user_repo),
    hasher=Depends(get_password_hasher),
    token_service: ITokenService = Depends(get_token_service),
    email_sender: IEmailSender = Depends(get_email_sender),
):
    if settings.app_env.lower() == "test":
        return CreateUser(repo, hasher)
    if isinstance(email_sender, NoopEmailSender):
        return CreateUser(repo, hasher)
    return CreateUser(
        repo,
        hasher,
        token_service,
        email_sender,
        settings.email_verification_url_base,
    )


def get_verify_user_email_uc(
    repo: IUserRepository = Depends(get_user_repo),
    token_service: ITokenService = Depends(get_token_service),
) -> VerifyUserEmail:
    return VerifyUserEmail(repo, token_service)


def get_login_user_uc(
    repo: IUserRepository = Depends(get_user_repo),
    hasher=Depends(get_password_hasher),
    token=Depends(get_token_service),
):
    return LoginUserUseCase(repo, hasher, token)


def get_refresh_token_uc(
    repo: IUserRepository = Depends(get_user_repo),
    token: ITokenService = Depends(get_token_service),
):
    return RefreshTokenUseCase(token, repo)


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


def get_list_tasks_with_validations_uc(
    task_repo: ITaskRepository = Depends(get_task_repo),
) -> ListTasksWithValidations:
    return ListTasksWithValidations(task_repo)


def get_get_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> GetTask:
    """Provide the GetTask use case."""
    return GetTask(repo)


def get_update_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> UpdateTask:
    """Provide the UpdateTask use case."""
    return UpdateTask(repo)


def get_assign_task_users_uc(
    task_repo: ITaskRepository = Depends(get_task_repo),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> AssignTaskUsers:
    return AssignTaskUsers(task_repo, user_repo)


def get_list_task_assignees_uc(
    task_repo: ITaskRepository = Depends(get_task_repo),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> ListTaskAssignees:
    return ListTaskAssignees(task_repo, user_repo)


def get_remove_task_user_uc(
    task_repo: ITaskRepository = Depends(get_task_repo),
) -> RemoveTaskUser:
    return RemoveTaskUser(task_repo)


def get_delete_task_uc(repo: ITaskRepository = Depends(get_task_repo)) -> DeleteTask:
    """Provide the DeleteTask use case."""
    return DeleteTask(repo)


# --- Task Validation


def get_task_validation_repo(
    session: AsyncSession = Depends(get_db),
) -> ITaskValidationRepository:
    """Provide repository for task validations."""
    return TaskValidationRepositorySQL(session)


def get_create_task_validation_uc(
    repo: ITaskValidationRepository = Depends(get_task_validation_repo),
) -> CreateTaskValidation:
    return CreateTaskValidation(repo)


def get_update_task_validation_uc(
    repo: ITaskValidationRepository = Depends(get_task_validation_repo),
) -> UpdateTaskValidation:
    return UpdateTaskValidation(repo)


def get_delete_task_validation_uc(
    repo: ITaskValidationRepository = Depends(get_task_validation_repo),
) -> DeleteTaskValidation:
    return DeleteTaskValidation(repo)


def get_list_task_validations_uc(
    repo: ITaskValidationRepository = Depends(get_task_validation_repo),
) -> ListTaskValidations:
    return ListTaskValidations(repo)
