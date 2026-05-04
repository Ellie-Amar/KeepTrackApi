from __future__ import annotations
from typing import Protocol
from uuid import UUID


class ITokenService(Protocol):
    """Verifying access tokens (JWT)."""

    def issue_access_token(self, *, user_id: UUID, email: str) -> str: ...

    """Return a compact access token string."""

    def issue_refresh_token(self, *, user_id: UUID, email: str) -> str: ...

    """Return a compact access/refresh token string."""

    def decode_access_token(self, token: str) -> dict: ...

    """Return token payload or raise a ValueError on invalid/expired token."""

    def decode_refresh_token(self, token: str) -> dict: ...

    """Return token payload or raise a ValueError on invalid/expired token."""

    def issue_email_verification_token(self, *, user_id: UUID, email: str) -> str: ...

    """Return a compact email verification token string."""

    def decode_email_verification_token(self, token: str) -> dict: ...

    """Return payload or raise a ValueError on invalid/expired token."""
