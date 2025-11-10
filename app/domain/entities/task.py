from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from app.domain.entities.base import BaseEntity
from app.domain.errors import ValidationError


@dataclass(frozen=True)
class Task(BaseEntity):
    """
    Dataclass for a task. It comes with its own domain rules within it.
    """

    owner_id: UUID
    label: str
    note: Optional[str] = None
    category: Optional[str] = None
    status: str = "active"  # enum eventually later
    order: int = 0

    def __post_init__(self):
        super().__post_init__()  # validates timestamps consistency and UTC from BaseEntity

        lbl = (self.label or "").strip()
        if not lbl:
            raise ValidationError("Task.label must not be empty")

        if self.order < 0:
            raise ValidationError("Task.order must be >= 0")

        # dataclass is frozen, so normalize via object.__setattr__
        object.__setattr__(self, "label", lbl)
