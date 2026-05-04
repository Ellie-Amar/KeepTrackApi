from __future__ import annotations

from uuid import UUID

from app.application.errors import AuthUserNotFoundError, InvalidTokenError
from app.application.ports.token_service import ITokenService
from app.application.ports.user_repository import IUserRepository
from app.domain.entities.user import User


class VerifyUserEmail:
    def __init__(self, repo: IUserRepository, token_service: ITokenService) -> None:
        self.repo = repo
        self.token_service = token_service

    async def execute(self, token: str) -> User:
        try:
            payload = self.token_service.decode_email_verification_token(token)
            user_id_raw = payload.get("sub")
            email = str(payload.get("email") or "").strip().lower()
            if not user_id_raw or not email:
                raise ValueError("Invalid token payload")
            user_id = UUID(str(user_id_raw))
        except ValueError as exc:
            raise InvalidTokenError("Invalid or expired verification token") from exc

        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise AuthUserNotFoundError("User not found")
        if user.email != email:
            raise InvalidTokenError("Invalid or expired verification token")
        if user.email_verified:
            return user

        verified_user = user.verify_email()
        await self.repo.update(verified_user)
        return verified_user
