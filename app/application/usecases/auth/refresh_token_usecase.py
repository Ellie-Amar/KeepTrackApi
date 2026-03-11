from __future__ import annotations
from uuid import UUID

from app.application.commands.refresh_token_command import RefreshTokenCommand
from app.application.errors import AuthUserNotFoundError, InvalidTokenError
from app.application.ports.token_service import ITokenService
from app.application.ports.user_repository import IUserRepository
from app.application.dto.auth_tokens import AuthTokens


class RefreshTokenUseCase:
    def __init__(
        self, token_service: ITokenService, user_repo: IUserRepository
    ) -> None:
        self.token_service = token_service
        self.user_repo = user_repo

    async def execute(self, cmd: RefreshTokenCommand) -> AuthTokens:
        """Validate refresh token and issue a new pair of tokens."""
        try:
            payload = self.token_service.decode_refresh_token(cmd.refresh_token)
            user_id_raw = payload.get("sub")
            if not user_id_raw:
                raise ValueError("Missing sub claim")
            user_id = UUID(str(user_id_raw))
        except ValueError:
            raise InvalidTokenError("Invalid or expired token")

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise AuthUserNotFoundError("User not found")

        return AuthTokens(
            access_token=self.token_service.issue_access_token(
                user_id=user.id, email=user.email
            ),
            refresh_token=self.token_service.issue_refresh_token(
                user_id=user.id, email=user.email
            ),
        )
