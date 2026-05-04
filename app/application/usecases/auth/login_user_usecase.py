from __future__ import annotations

from app.application.commands.login_user_command import LoginUserCommand
from app.application.errors import EmailNotVerifiedError, InvalidCredentialsError
from app.application.ports.user_repository import IUserRepository
from app.application.ports.password_hasher import IPasswordHasher
from app.application.ports.token_service import ITokenService
from app.application.dto.auth_tokens import AuthTokens


class LoginUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher
        self.token_service = token_service

    async def execute(self, cmd: LoginUserCommand) -> AuthTokens:
        """Authenticate user and return JWT tokens."""
        user = await self.user_repo.get_by_email(cmd.email)
        if user is None or not self.hasher.verify(cmd.password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")
        if not user.email_verified:
            raise EmailNotVerifiedError("Email not verified")

        return AuthTokens(
            access_token=self.token_service.issue_access_token(
                user_id=user.id,
                email=user.email,
            ),
            refresh_token=self.token_service.issue_refresh_token(
                user_id=user.id,
                email=user.email,
            ),
        )
