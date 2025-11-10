from __future__ import annotations
from typing import Final
from argon2 import PasswordHasher
from argon2.low_level import Type
from app.application.ports.password_hasher import IPasswordHasher

_PH: Final = PasswordHasher(
    time_cost=3,
    memory_cost=64_000,
    parallelism=2,
    hash_len=32,
    salt_len=16,
    type=Type.ID,
)


class Argon2PasswordHasher(IPasswordHasher):
    """Hash & verify passwords with Argon2id."""

    def hash(self, password: str) -> str:
        if not isinstance(password, str):
            raise TypeError("password must be a string")
        return _PH.hash(password)

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return _PH.verify(password_hash, password)
        except Exception:
            return False
