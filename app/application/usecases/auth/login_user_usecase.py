from __future__ import annotations

from fastapi import HTTPException, status

from app.application.commands.login_user_command import LoginUserCommand
from app.application.ports.user_repository import IUserRepository
from app.application.ports.password_hasher import IPasswordHasher
from app.application.ports.token_service import ITokenService


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

    async def execute(self, cmd: LoginUserCommand) -> str:
        """Authenticate user and return JWT token."""
        user = await self.user_repo.get_by_email(cmd.email)
        if user is None or not self.hasher.verify(cmd.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return self.token_service.issue_access_token(
            user_id=user.id,
            email=user.email,
        )
