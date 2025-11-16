from __future__ import annotations
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.application.ports.task_repository import ITaskRepository
from app.domain.entities.task import Task, TaskWithValidations
from app.domain.entities.user import User
from app.interfaces.dependencies import get_task_repo, get_token_service, get_user_repo
from app.application.ports.token_service import ITokenService
from app.application.ports.user_repository import IUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    token_service: ITokenService = Depends(get_token_service),
    user_repo: IUserRepository = Depends(get_user_repo),
) -> User | None:
    """Decode JWT, fetch user, raise 401 if invalid."""
    try:
        payload = token_service.decode_access_token(token)
        user_id_raw = payload.get("sub")
        if not user_id_raw:
            raise ValueError("Missing sub claim")
        user_id = UUID(str(user_id_raw))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def require_task_access(
    task_id: UUID,
    repo: ITaskRepository = Depends(get_task_repo),
    current_user=Depends(get_current_user),
) -> Task | None:
    """
    - Check if task exsists
    - Authorize access if owner or participant
    - Else 404
    """
    task = await repo.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    if task.owner_id == current_user.id:
        return task

    user_task_list = await repo.list_by_user(current_user.id)
    if any(t.id == task_id for t in user_task_list):
        return task

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


async def require_task_with_validations(
    task_id: UUID,
    repo: ITaskRepository = Depends(get_task_repo),
    current_user=Depends(get_current_user),
) -> TaskWithValidations:
    entry = await repo.get_with_validations(task_id)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    task = entry.task
    if task.owner_id == current_user.id:
        return entry

    user_task_list = await repo.list_by_user(current_user.id)
    if any(t.id == task_id for t in user_task_list):
        return entry

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
