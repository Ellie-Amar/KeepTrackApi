from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt  # PyJWT

from app.application.ports.token_service import ITokenService


class JwtTokenService(ITokenService):
    """
    Lightweight JWT adapter.

    Notes:
    - Uses HS256 by default (shared secret).
    - Raises ValueError on invalid or expired tokens.
    """

    def __init__(
        self,
        *,
        secret: str,
        issuer: str = "keeptrack",
        algorithm: str = "HS256",
        access_ttl: timedelta = timedelta(minutes=60),
    ) -> None:
        if not secret:
            raise ValueError("JWT secret must be provided")
        self._secret = secret
        self._issuer = issuer
        self._alg = algorithm
        self._ttl = access_ttl

    def issue_access_token(self, *, user_id: UUID, email: str) -> str:
        now = datetime.now(timezone.utc)
        payload: dict[str, Any] = {
            "sub": str(user_id),
            "email": email.lower(),
            "iss": self._issuer,
            "iat": int(now.timestamp()),
            "exp": int((now + self._ttl).timestamp()),
            "type": "access",
        }
        return jwt.encode(payload, self._secret, algorithm=self._alg)

    def decode_access_token(self, token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self._alg],
                options={"require": ["exp", "iat", "iss"]},
                issuer=self._issuer,
                leeway=0, # lag tolerance
            )
            if payload.get("type") != "access":
                raise ValueError("Invalid token type")
            return payload
        except jwt.PyJWTError as e:
            raise ValueError(str(e)) from e
