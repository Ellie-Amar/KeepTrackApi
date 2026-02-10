from __future__ import annotations


class StubHasher:
    def hash(self, password: str) -> str:
        return f"hashed::{password}"

    def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == self.hash(password)


class StubTokenService:
    def __init__(self, *, payload: dict | None = None, error: ValueError | None = None):
        self.payload = payload
        self.error = error

    def issue_access_token(self, *, user_id, email) -> str:  # type: ignore[override]
        return f"token::{user_id}"

    def issue_refresh_token(self, *, user_id, email) -> str:  # type: ignore[override]
        return f"refresh::{user_id}"

    def decode_access_token(self, token: str) -> dict:
        if self.error is not None:
            raise self.error
        if self.payload is None:
            raise ValueError("No payload configured for StubTokenService")
        return self.payload

    def decode_refresh_token(self, token: str) -> dict:
        if self.error is not None:
            raise self.error
        if self.payload is None:
            raise ValueError("No payload configured for StubTokenService")
        return self.payload
