from __future__ import annotations

import dataclasses
from dataclasses import dataclass

from app.domain.entities.base import BaseEntity
from app.domain.errors import ValidationError


@dataclass(frozen=True, slots=True)
class User(BaseEntity):
    """
    Dataclass for a task. It comes with its own domain rules within it.
    """

    email: str
    password_hash: str
    display_name: str | None = None
    is_active: bool = True
    email_verified: bool = False

    def __post_init__(self) -> None:
        BaseEntity.__post_init__(
            self
        )  # validates timestamps consistency and UTC from BaseEntity

        # normalize and validate email
        normalized = (self.email or "").strip().lower()
        if not normalized or "@" not in normalized:
            raise ValidationError("Invalid email")
        object.__setattr__(self, "email", normalized)

        # small guard on password hash
        if not isinstance(self.password_hash, str) or not self.password_hash.strip():
            raise ValidationError("password_hash must be a non-empty string")

    # --- Mutators ---

    def with_display_name(self, display_name: str | None) -> User:
        """Return a copy with updated display name and bumped updated_at."""
        new_display = (display_name.strip() or None) if display_name else None
        return dataclasses.replace(self, display_name=new_display).bump_updated_at()

    def activate(self) -> User:
        """Return a copy marked as active (no-op if already active)."""
        if self.is_active:
            return self
        return dataclasses.replace(self, is_active=True).bump_updated_at()

    def deactivate(self) -> User:
        """Return a copy marked as inactive (no-op if already inactive)."""
        if not self.is_active:
            return self
        return dataclasses.replace(self, is_active=False).bump_updated_at()

    def with_email(self, new_email: str) -> User:
        """Return a copy with a normalized/validated email and bumped updated_at."""
        normalized = (new_email or "").strip().lower()
        if not normalized or "@" not in normalized:
            raise ValidationError("Invalid email")
        return dataclasses.replace(self, email=normalized).bump_updated_at()

    def with_password_hash(self, new_hash: str) -> User:
        """Return a copy with a new password hash and bumped updated_at."""
        if not isinstance(new_hash, str) or not new_hash.strip():
            raise ValidationError("password_hash must be a non-empty string")
        return dataclasses.replace(self, password_hash=new_hash).bump_updated_at()

    def verify_email(self) -> User:
        """Return a copy with verified email and bumped updated_at."""
        if self.email_verified:
            return self
        return dataclasses.replace(self, email_verified=True).bump_updated_at()
