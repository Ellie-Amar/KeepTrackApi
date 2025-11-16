from __future__ import annotations

from datetime import datetime
from uuid import UUID

from app.domain.entities.task_validation import TaskValidation
from app.domain.entities.user import User
from app.interfaces.view_models.base_view_model import ViewModel


class TaskValidationCreate(ViewModel):
    note: str | None = None


class TaskValidationUser(ViewModel):
    id: UUID
    display_name: str | None = None


class TaskValidationRead(ViewModel):
    id: UUID
    task_id: UUID
    note: str | None
    created_at: datetime
    updated_at: datetime
    user: TaskValidationUser

    @classmethod
    def from_entity(
        cls, validation: TaskValidation, *, display_name: str | None = None
    ) -> TaskValidationRead:
        return cls(
            id=validation.id,
            task_id=validation.task_id,
            note=validation.note,
            created_at=validation.created_at,
            updated_at=validation.updated_at,
            user=TaskValidationUser(
                id=validation.user_id,
                display_name=display_name,
            ),
        )

    @classmethod
    def from_entity_for_user(
        cls, validation: TaskValidation, current_user: User | None
    ) -> TaskValidationRead:
        display_name = validation.user_display_name
        if (
            display_name is None
            and current_user
            and current_user.id == validation.user_id
        ):
            display_name = current_user.display_name
        return cls.from_entity(validation, display_name=display_name)


class TaskValidationUpdate(ViewModel):
    note: str | None = None
