from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.application.errors import (
    AuthUserNotFoundError,
    EmailDeliveryError,
    InvalidTokenError,
)
from app.domain.errors import ValidationError
from app.application.usecases.user.create_user_usecase import CreateUser
from app.application.usecases.user.verify_user_email_usecase import VerifyUserEmail
from app.interfaces.dependencies import get_create_user_uc, get_verify_user_email_uc
from app.interfaces.rate_limit import limiter
from app.interfaces.view_models.user_view_model import UserCreate, UserRead

router = APIRouter(prefix="/v1/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def create_user(
    request: Request,
    payload: UserCreate,
    uc: CreateUser = Depends(get_create_user_uc),
):
    try:
        user = await uc.execute(
            email=payload.email,
            password=payload.password,
            display_name=payload.display_name,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return user


@router.get("/verify-email", response_model=UserRead)
@limiter.limit("10/minute")
async def verify_user_email(
    request: Request,
    token: str,
    uc: VerifyUserEmail = Depends(get_verify_user_email_uc),
):
    try:
        user = await uc.execute(token)
    except InvalidTokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except AuthUserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return user
