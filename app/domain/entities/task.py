from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from app.domain.errors import ValidationError

@dataclass(frozen=True)
class Task:
    """
    Dataclass for a task (o rly?).
    """
    id: UUID
    user_id: UUID
    label: str
    note: Optional[str] = None
    category: Optional[str] = None
    status: str = "active"  # enum later
    order: int = 0
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    def __post_init__(self):
        # normalize label
        lbl = (self.label or "").strip()

        # validate domain rules
        if not lbl:
            raise ValidationError("Task.label must not be empty")

        if self.order < 0:
            raise ValidationError("Task.order must be >= 0")

        if self.created_at > self.updated_at:
            raise ValidationError("Task.created_at cannot be after updated_at")

        # dataclass is frozen, so we use object.__setattr__ for normalization
        object.__setattr__(self, "label", lbl)

    @classmethod
    def new(cls, user_id: UUID, label: str,
            note: Optional[str] = None,
            category: Optional[str] = None,
            order: int = 0) -> "Task":
        """
        Factory method to create a new Task.
        Automatically assigns uuid and timestamps.
        """
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            user_id=user_id,
            label=label,
            note=note,
            category=category,
            order=order,
            created_at=now,
            updated_at=now,
        )
