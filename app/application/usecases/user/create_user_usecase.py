from __future__ import annotations
from urllib.parse import urlencode

from app.application.errors import EmailDeliveryError
from app.application.ports.email_sender import IEmailSender
from app.application.ports.token_service import ITokenService
from app.application.ports.user_repository import IUserRepository
from app.application.ports.password_hasher import IPasswordHasher
from app.domain.entities.user import User
from app.domain.errors import ValidationError


class CreateUser:
    def __init__(
        self,
        repo: IUserRepository,
        hasher: IPasswordHasher,
        token_service: ITokenService | None = None,
        email_sender: IEmailSender | None = None,
        verification_url_base: str | None = None,
    ) -> None:
        self.repo = repo
        self.hasher = hasher
        self.token_service = token_service
        self.email_sender = email_sender
        self.verification_url_base = verification_url_base
        self._verification_enabled = (
            token_service is not None
            and email_sender is not None
            and bool(verification_url_base)
        )

    async def execute(
        self, email: str, password: str, display_name: str | None = None
    ) -> User:

        if not password or len(password) < 8:
            raise ValidationError("Password too short")

        if await self.repo.get_by_email(email.lower()):
            raise ValidationError("Email already exists")

        password_hash = self.hasher.hash(password)
        user = User.new(
            email=email,
            password_hash=password_hash,
            display_name=display_name,
            email_verified=not self._verification_enabled,
        )
        await self.repo.add(user)
        await self._send_verification_email(user)
        return user

    async def _send_verification_email(self, user: User) -> None:
        if not self._verification_enabled:
            return

        assert self.token_service is not None
        assert self.email_sender is not None
        assert self.verification_url_base is not None
        token = self.token_service.issue_email_verification_token(
            user_id=user.id,
            email=user.email,
        )
        verify_url = f"{self.verification_url_base}?{urlencode({'token': token})}"
        subject = "Confirmez votre adresse email"
        text_body = (
            "Bienvenue sur KeepTrack.\n\n"
            "Cliquez sur ce lien pour verifier votre adresse email :\n"
            f"{verify_url}\n\n"
            "Si vous n'etes pas a l'origine de cette inscription, ignorez cet email."
        )
        try:
            await self.email_sender.send(
                to_email=user.email,
                subject=subject,
                text_body=text_body,
            )
        except Exception as exc:
            raise EmailDeliveryError("Unable to send verification email") from exc
