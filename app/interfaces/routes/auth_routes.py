from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.application.commands.login_user_command import LoginUserCommand
from app.application.commands.refresh_token_command import RefreshTokenCommand
from app.application.usecases.auth.login_user_usecase import LoginUserUseCase
from app.application.usecases.auth.refresh_token_usecase import RefreshTokenUseCase
from app.interfaces.dependencies import get_login_user_uc, get_refresh_token_uc
from app.interfaces.view_models.auth_view_model import (
    RefreshTokenRequest,
    TokenResponse,
)

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uc: LoginUserUseCase = Depends(get_login_user_uc),
):
    """Authenticate user and return JWT token."""
    tokens = await uc.execute(
        LoginUserCommand(email=form_data.username, password=form_data.password)
    )
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    body: RefreshTokenRequest,
    uc: RefreshTokenUseCase = Depends(get_refresh_token_uc),
):
    tokens = await uc.execute(RefreshTokenCommand(refresh_token=body.refresh_token))
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type="bearer",
    )
