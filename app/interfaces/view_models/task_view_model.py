from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.domain.entities.task import TaskWithValidations
from app.domain.entities.user import User
from app.interfaces.view_models.base_view_model import ViewModel
from app.interfaces.view_models.task_validation_view_model import TaskValidationRead


class TaskCreate(ViewModel):
    label: str = Field(..., min_length=1)
    note: str | None = None
    category: str | None = None
    order: int = 0


class TaskRead(ViewModel):
    id: UUID
    owner_id: UUID
    label: str
    note: str | None
    category: str | None
    status: str
    order: int | None
    created_at: datetime
    updated_at: datetime
    validations: list[TaskValidationRead] = Field(default_factory=list)

    @classmethod
    def from_task_with_validations(
        cls, item: TaskWithValidations, current_user: User | None = None
    ) -> TaskRead:
        return cls(
            id=item.task.id,
            owner_id=item.task.owner_id,
            label=item.task.label,
            note=item.task.note,
            category=item.task.category,
            status=item.task.status,
            order=item.task.order,
            created_at=item.task.created_at,
            updated_at=item.task.updated_at,
            validations=[
                TaskValidationRead.from_entity_for_user(validation, current_user)
                for validation in item.validations
            ],
        )


class TaskUpdate(ViewModel):
    label: Optional[str] = Field(default=None, min_length=1)
    note: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    order: Optional[int] = None
