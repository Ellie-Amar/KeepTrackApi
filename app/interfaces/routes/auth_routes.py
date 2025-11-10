from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.application.commands.login_user_command import LoginUserCommand
from app.application.usecases.auth.login_user_usecase import LoginUserUseCase
from app.interfaces.dependencies import get_login_user_uc
from app.interfaces.view_models.auth_view_model import TokenResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    uc: LoginUserUseCase = Depends(get_login_user_uc),
):
    """Authenticate user and return JWT token."""
    token = await uc.execute(
        LoginUserCommand(email=form_data.username, password=form_data.password)
    )
    return TokenResponse(access_token=token, token_type="bearer")
