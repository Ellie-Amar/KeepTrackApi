from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self
from uuid import UUID, uuid4

from app.domain.errors import ValidationError


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True, slots=True, kw_only=True)
class BaseEntity:
    id: UUID
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)

    def __post_init__(self) -> None:
        # Ensure timezone timestamps (UTC)
        for name in ("created_at", "updated_at"):
            dt: datetime = getattr(self, name)
            if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
                raise ValidationError(f"{name} must be timezone-aware (UTC)")
        if self.updated_at < self.created_at:
            raise ValidationError("updated_at must be >= created_at")

    @classmethod
    def new(cls: type[Self], **kwargs: Any) -> Self:
        """Generic factory: generates id and timestamps, forwards subclass fields."""
        now = _utcnow()
        return cls(id=uuid4(), created_at=now, updated_at=now, **kwargs)

    def bump_updated_at(self) -> Self:
        """Return a copy with updated_at bumped to now."""
        return dataclasses.replace(self, updated_at=_utcnow())
