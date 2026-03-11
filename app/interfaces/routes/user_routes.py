from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.errors import ValidationError
from app.application.usecases.user.create_user_usecase import CreateUser
from app.interfaces.dependencies import get_create_user_uc
from app.interfaces.view_models.user_view_model import UserCreate, UserRead

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate, uc: CreateUser = Depends(get_create_user_uc)
):
    try:
        user = await uc.execute(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return user
